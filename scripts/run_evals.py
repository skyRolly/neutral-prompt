#!/usr/bin/env python3
"""Measure scan_prompt.py against the labeled cases in evals/cases.jsonl.

Every case carries the exact set of rule ids the scanner is expected to report.
`validate` checks the case file; `scan` runs the scanner over every case and
compares the result to the label, then reports per-rule recall, the aggregate
counts, and the cases marked as known scanner limitations.

The harness runs offline and calls no model. It measures the detector, not an
agent's rewrites -- for that, see evals/rubric.md.

Usage:
    python3 scripts/run_evals.py validate
    python3 scripts/run_evals.py scan
    python3 scripts/run_evals.py scan --json

Exit codes:
    0  every case matched its label
    1  at least one case did not match, or the case file is invalid
    2  usage or input error
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scan_prompt import COVERAGE_RULE, RULES_BY_ID, scan_text  # noqa: E402

CASES_PATH = ROOT / "evals" / "cases.jsonl"
KNOWN_RULE_IDS = set(RULES_BY_ID) | {COVERAGE_RULE.id}
REQUIRED_FIELDS = ("id", "category", "kind", "text", "expect", "note")
VALID_KINDS = ("directional", "neutral")
VALID_CATEGORIES = ("lifecycle", "review", "investigation", "accept-reject", "general")


def load_cases(path: Path) -> list[dict]:
    """Parse cases.jsonl, one JSON object per non-empty line."""
    cases: list[dict] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            cases.append(json.loads(stripped))
        except json.JSONDecodeError as error:
            raise ValueError(f"{path}:{number}: invalid JSON: {error}") from error
    return cases


def validate_cases(cases: list[dict]) -> list[str]:
    """Return one message per schema problem; an empty list means valid."""
    problems: list[str] = []
    seen: set[str] = set()

    for index, case in enumerate(cases, 1):
        label = case.get("id", f"<case {index}>")

        missing = [field for field in REQUIRED_FIELDS if field not in case]
        if missing:
            problems.append(f"{label}: missing field(s): {', '.join(missing)}")
            continue

        if case["id"] in seen:
            problems.append(f"{label}: duplicate id")
        seen.add(case["id"])

        if case["kind"] not in VALID_KINDS:
            problems.append(f"{label}: kind must be one of {VALID_KINDS}")

        if case["category"] not in VALID_CATEGORIES:
            problems.append(f"{label}: category must be one of {VALID_CATEGORIES}")

        if not isinstance(case["text"], str) or not case["text"].strip():
            problems.append(f"{label}: text must be a non-empty string")

        if not isinstance(case["expect"], list):
            problems.append(f"{label}: expect must be a list of rule ids")
            continue

        unknown = [rid for rid in case["expect"] if rid not in KNOWN_RULE_IDS]
        if unknown:
            problems.append(f"{label}: unknown rule id(s): {', '.join(unknown)}")

        if len(set(case["expect"])) != len(case["expect"]):
            problems.append(f"{label}: duplicate rule ids in expect")

        if case["kind"] == "directional" and not case["expect"]:
            problems.append(f"{label}: a directional case expects at least one rule")

        if not isinstance(case["note"], str) or not case["note"].strip():
            problems.append(f"{label}: note must explain the label")

    return problems


def evaluate(cases: list[dict]) -> dict:
    """Run the scanner over every case and compare to its label."""
    results = []
    for case in cases:
        found = sorted({finding.rule_id for finding in scan_text(case["text"], case["id"])})
        expected = sorted(set(case["expect"]))
        results.append(
            {
                "id": case["id"],
                "category": case["category"],
                "kind": case["kind"],
                "expected": expected,
                "found": found,
                "missed": [rid for rid in expected if rid not in found],
                "extra": [rid for rid in found if rid not in expected],
                "matched": found == expected,
                "known_limitation": case["kind"] == "neutral" and bool(expected),
            }
        )

    per_rule: dict[str, dict[str, int]] = {}
    for result in results:
        for rid in result["expected"]:
            row = per_rule.setdefault(rid, {"expected": 0, "detected": 0})
            row["expected"] += 1
            if rid in result["found"]:
                row["detected"] += 1

    return {
        "cases": len(results),
        "matched": sum(1 for r in results if r["matched"]),
        "mismatched": [r for r in results if not r["matched"]],
        "known_limitations": [r for r in results if r["known_limitation"]],
        "per_rule": per_rule,
        "results": results,
    }


def rules_without_coverage(per_rule: dict[str, dict[str, int]]) -> list[str]:
    return sorted(rid for rid in KNOWN_RULE_IDS if rid not in per_rule)


def print_report(report: dict) -> None:
    print(f"cases: {report['cases']}  matched: {report['matched']}")

    print("\nper-rule recall (detected / labeled):")
    for rid in sorted(report["per_rule"]):
        row = report["per_rule"][rid]
        title = RULES_BY_ID[rid].title if rid in RULES_BY_ID else COVERAGE_RULE.title
        print(f"  {rid}  {row['detected']}/{row['expected']}  {title}")

    uncovered = rules_without_coverage(report["per_rule"])
    if uncovered:
        print("\nrules with no labeled case: " + ", ".join(uncovered))

    if report["known_limitations"]:
        print("\nknown scanner limitations (neutral text the scanner still flags):")
        for result in report["known_limitations"]:
            print(f"  {result['id']}: flags {', '.join(result['expected'])}")

    if report["mismatched"]:
        print("\nmismatched cases:")
        for result in report["mismatched"]:
            print(f"  {result['id']}")
            if result["missed"]:
                print(f"    not detected: {', '.join(result['missed'])}")
            if result["extra"]:
                print(f"    unexpected:   {', '.join(result['extra'])}")
    else:
        print("\nall cases matched their labels")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="run_evals.py",
        description="Measure scan_prompt.py against evals/cases.jsonl.",
    )
    parser.add_argument("command", choices=("validate", "scan"))
    parser.add_argument(
        "--cases", default=str(CASES_PATH), help="path to the case file"
    )
    parser.add_argument("--json", action="store_true", help="emit a JSON report")
    args = parser.parse_args(argv)

    try:
        cases = load_cases(Path(args.cases))
    except FileNotFoundError:
        print(f"run_evals.py: no such file: {args.cases}", file=sys.stderr)
        return 2
    except ValueError as error:
        print(f"run_evals.py: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"run_evals.py: cannot read {args.cases}: {error}", file=sys.stderr)
        return 2

    problems = validate_cases(cases)
    if problems:
        for problem in problems:
            print(f"run_evals.py: {problem}", file=sys.stderr)
        return 1

    if args.command == "validate":
        print(f"{len(cases)} case(s) valid")
        return 0

    report = evaluate(cases)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)
    return 0 if not report["mismatched"] else 1


if __name__ == "__main__":
    sys.exit(main())
