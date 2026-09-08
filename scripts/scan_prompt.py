#!/usr/bin/env python3
"""Scan prompt text for directional wording.

Reports phrasings that raise the prior on one outcome before an agent has
evaluated anything. Every rule maps to an entry in
skills/neutral-prompts/references/patterns.md, which explains the mechanism and
gives a neutral replacement.

The scanner finds phrasings, not intent. A hit on a settled constraint (a safety
rule, an output contract, a budget) is correct as written -- confirm what each
phrase governs before rewriting it, and suppress the ones that are fine.

Usage:
    python3 scripts/scan_prompt.py PROMPT.md [MORE.md ...]
    cat prompt.txt | python3 scripts/scan_prompt.py -
    python3 scripts/scan_prompt.py --json prompt.md
    python3 scripts/scan_prompt.py --list-rules

Suppression:
    Put `neutral-prompts: allow NP003` (or `allow all`) on the flagged line or
    on the line directly above it. Several ids may be listed, comma-separated.

Exit codes:
    0  no findings at or above --fail-on
    1  findings at or above --fail-on
    2  usage or input error
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

SEVERITIES = ("advisory", "medium", "high")
SEVERITY_RANK = {name: index for index, name in enumerate(SEVERITIES)}

SUPPRESS_RE = re.compile(
    r"neutral-prompts:\s*allow\s+(all|NP\d{3}(?:\s*,\s*NP\d{3})*)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Rule:
    """One directional-wording pattern."""

    id: str
    title: str
    severity: str
    why: str
    suggestion: str
    patterns: tuple[str, ...]
    regex: re.Pattern[str] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        joined = "|".join(f"(?:{pattern})" for pattern in self.patterns)
        object.__setattr__(self, "regex", re.compile(joined, re.IGNORECASE))


RULES: tuple[Rule, ...] = (
    Rule(
        id="NP001",
        title="protected stop",
        severity="high",
        why="A negated stop verb protects continuation: the complement becomes the default and needs no justification.",
        suggestion="Name the decision instead: 'Evaluate each one. Continuing and stopping are both admissible outcomes.'",
        patterns=(
            r"\b(?:do\s+not|don'?t|never|avoid|refrain\s+from)\s+(?:\w+\s+){0,3}?"
            r"(?:stops?|stopping|halts?|halting|terminates?|terminating|kills?|killing|"
            r"aborts?|aborting|cancels?|cancell?ing|interrupts?|interrupting|"
            r"shut(?:s|ting)?\s+down)\b",
        ),
    ),
    Rule(
        id="NP002",
        title="protected continuation",
        severity="high",
        why="Stopping becomes conditional on a finish line the agent usually cannot observe, so continuing is the only compliant action.",
        suggestion="Bound it by information: 'Continue while the next step can answer a named open question; stop when none remains.'",
        patterns=(
            r"\b(?:continue|keep\s+(?:going|running|working|iterating|digging|searching))"
            r"(?:\s+\w+){0,3}?\s+until\b",
            r"\buntil\s+(?:[\w-]+\s+){0,3}?(?:it\s+)?(?:is\s+|are\s+)?"
            r"(?:complete|completed|done|finished|fully\s+resolved)\b",
            r"\bkeep\s+(?:the\s+|them\s+|it\s+|all\s+)?(?:[\w-]+\s+){0,2}?alive\b",
            r"\b(?:do\s+not|don'?t|never)\s+give\s+up\b",
            r"\bkeep\s+going\b",
        ),
    ),
    Rule(
        id="NP003",
        title="protected preservation",
        severity="high",
        why="'Unnecessary' is decided after the fact, so the agent applies it in advance to everything and treats existing code as evidence for itself.",
        suggestion="State the criterion: 'Change when justified by evidence, requirements, correctness, maintainability, or user impact; preserve otherwise.'",
        patterns=(
            r"\b(?:do\s+not|don'?t|never|avoid)\s+(?:\w+\s+){0,3}?"
            r"(?:modif(?:y|ies|ying)|change[sd]?|changing|refactor(?:s|ed|ing)?|"
            r"touch(?:es|ing)?|rewrit(?:e|es|ing)|restructur(?:e|es|ing))\b",
            r"\bunnecessary\s+(?:changes|modifications|edits|refactor\w*|rewrites)\b",
            r"\bleave\s+(?:it|them|things|the\s+(?:[\w-]+\s+){0,3}?[\w-]+)\s+"
            r"(?:as[-\s]is|alone|untouched)\b",
            r"\bminimal\s+(?:changes|edits|diff)\b",
            r"\bkeep\s+(?:the\s+)?(?:diff|changes?|edits?|footprint)\s+"
            r"(?:as\s+)?(?:minimal|small)\b",
            r"\bas\s+few\s+changes\s+as\s+possible\b",
        ),
    ),
    Rule(
        id="NP004",
        title="mandatory change",
        severity="high",
        why="Converts a scoping decision into an obligation, so out-of-scope and incorrect findings get acted on too.",
        suggestion="Open the disposition: 'For each finding: fix, defer with a tracked follow-up, or reject with counter-evidence.'",
        patterns=(
            r"\b(?:must|always|make\s+sure\s+(?:to|you|that\s+you)|be\s+sure\s+to|"
            r"ensure\s+(?:you|to|that\s+you))\s+(?:\w+\s+){0,2}?"
            r"(?:fix|fixes|address|addresses|resolve|resolves|correct|corrects)\b",
            r"\bfix\s+(?:all|every|any\s+and\s+all|each\s+and\s+every)\b",
            r"\bevery\s+(?:finding|issue|comment|suggestion)\s+must\s+be\b",
        ),
    ),
    Rule(
        id="NP005",
        title="forced acceptance",
        severity="high",
        why="Replaces evaluation with authorship: the agent stops checking whether a claim is true and starts checking who made it.",
        suggestion="Evaluate on the merits: 'Verify each suggestion against the code and the requirements; accept, reject with counter-evidence, or defer.'",
        patterns=(
            r"\b(?:always|must)\s+(?:accept|approve|apply|follow|implement)\b",
            r"\b(?:do\s+not|don'?t|never)\s+(?:\w+\s+){0,2}?"
            r"(?:reject|refuse|question|challenge|dispute|disagree|push\s+back)\b",
            r"\bdefer\s+to\s+the\s+(?:reviewer|architect|author|maintainer|senior|lead)\b",
        ),
    ),
    Rule(
        id="NP006",
        title="forced rejection",
        severity="medium",
        why="The mirror of forced acceptance. A prompt hardened against bad suggestions is equally hardened against good ones.",
        suggestion="Treat findings as claims to verify: 'Reproduce before accepting; state what failed to reproduce before rejecting.'",
        patterns=(
            r"\b(?:always|must)\s+(?:reject|refuse|dismiss|discard)\b",
            r"\b(?:do\s+not|don'?t|never)\s+(?:\w+\s+){0,2}?(?:accept|trust|believe)\b",
            r"\bignore\s+(?:any|all|every|automated)\b",
        ),
    ),
    Rule(
        id="NP007",
        title="asymmetric burden of proof",
        severity="high",
        why="One outcome needs certainty and the other needs nothing. That is a ranking wearing the clothes of a criterion.",
        suggestion="Give both sides an observable condition and ask for confidence on whichever is chosen.",
        patterns=(
            r"\bunless\s+(?:it\s+is\s+|it'?s\s+)?(?:absolutely|strictly|truly|really)\b",
            r"\bonly\s+(?:if|when)\s+(?:absolutely|strictly|truly)\b",
            r"\bunless\s+you\s+are\s+(?:absolutely\s+|completely\s+|really\s+)?"
            r"(?:sure|certain|confident|positive)\b",
            r"\bonly\s+(?:if|when)\s+you\s+are\s+(?:absolutely\s+|completely\s+)?"
            r"(?:sure|certain|confident)\b",
            r"\bat\s+all\s+costs\b",
            r"\bunder\s+no\s+circumstances\b",
            r"\babsolutely\s+necessary\b",
        ),
    ),
    Rule(
        id="NP008",
        title="loaded error label",
        severity="high",
        why="The label names one outcome as the error mode. Both directions have a cost; naming only one hides the other.",
        suggestion="Name both failure modes and ask which risk dominates here, with the reason.",
        patterns=(
            r"\bpremature(?:ly)?\b",
            r"\btoo\s+(?:early|soon|quickly|hastily)\b",
            r"\berr\s+on\s+the\s+side\s+of\b",
            r"\b(?:do\s+not|don'?t)\s+be\s+(?:lazy|timid|shy|conservative|aggressive|hasty|sloppy)\b",
            r"\bbail(?:ing)?\s+out\b",
        ),
    ),
    Rule(
        id="NP009",
        title="unbounded effort",
        severity="medium",
        why="Prices the next step at zero. With no cost on the ledger, more work always wins the comparison.",
        suggestion="Bound it by expected information gain and name the question each step is meant to answer.",
        patterns=(
            r"\bbe\s+(?:thorough|exhaustive|comprehensive)\b",
            r"\b(?:thoroughly|exhaustively)\b",
            r"\bexhaustive\b",
            r"\bleave\s+no\s+stone\s+unturned\b",
            r"\bas\s+(?:much|many|thorough|deeply?)\s+as\s+possible\b",
            r"\bkeep\s+digging\b",
            r"\b(?:explore|check|investigate|review)\s+(?:everything|all\s+avenues|every\s+possibility)\b",
        ),
    ),
    Rule(
        id="NP010",
        title="unobservable threshold",
        severity="medium",
        why="A criterion the agent cannot check against the workspace resolves to whatever the surrounding wording already implied.",
        suggestion="Replace with something checkable: a count, a file, a test, a time budget, or a named condition.",
        patterns=(
            r"\b(?:enough|sufficient|sufficiently|significant|significantly|"
            r"substantial|substantially|reasonable|reasonably|meaningful)\b",
            r"\bas\s+needed\b",
            r"\bif\s+necessary\b",
            r"\b(?:where|as|when)\s+appropriate\b",
            r"\bwhen\s+it\s+makes\s+sense\b",
        ),
    ),
    Rule(
        id="NP011",
        title="required conclusion",
        severity="high",
        why="The reasoning request accepts exactly one outcome, so an agent that would have chosen differently must contradict the prompt to report honestly.",
        suggestion="Ask for the record instead: evidence considered, alternatives compared, action selected, and why it beat the alternatives.",
        patterns=(
            r"\bexplain\s+(?:why|how)\s+(?:you|it|this|that|the\s+\w+)\s+"
            r"(?:\w+\s+){0,2}?(?:kept|continued|stopped|fixed|accepted|rejected|"
            r"works?|will\s+work|is\s+correct|is\s+right|is\s+better|is\s+safe)\b",
            r"\bconfirm\s+that\s+(?:this|it|that|the\s+\w+)\s+(?:is|was|will\s+be)\s+"
            r"(?:correct|right|the\s+right|fine|safe|sound|appropriate)\b",
            r"\bjustify\s+(?:keeping|continuing|stopping|fixing|accepting|rejecting|"
            r"preserving|changing)\b",
        ),
    ),
)

RULES_BY_ID = {rule.id: rule for rule in RULES}

COVERAGE_RULE = Rule(
    id="NP012",
    title="missing counterweight",
    severity="advisory",
    why="The text delegates a lifecycle or review decision but states no criteria, so the agent falls back on tone, on its own defaults, or on whichever outcome was named first.",
    suggestion="Name the admissible outcomes and the observable condition that selects each one.",
    patterns=(r"(?!x)x",),  # never matched per line; evaluated over the whole document
)

DECISION_VERBS = re.compile(
    r"\b(?:stop|stopping|continue|continuing|terminate|proceed|accept|reject|"
    r"approve|fix|refactor|preserve|defer|decide|keep\s+running|shut\s+down)\b",
    re.IGNORECASE,
)
CRITERIA_MARKERS = re.compile(
    r"\b(?:criteri(?:a|on)|evidence|outcomes?|if\b|when\b|whether\b|unless\b|"
    r"based\s+on|threshold|trade[-\s]?off|expected\s+value|because)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    column: int
    rule_id: str
    severity: str
    text: str
    why: str
    suggestion: str

    def as_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "line": self.line,
            "column": self.column,
            "rule": self.rule_id,
            "severity": self.severity,
            "text": self.text,
            "why": self.why,
            "suggestion": self.suggestion,
        }


def suppressed_ids(line: str) -> set[str]:
    """Return the rule ids suppressed by a comment on this line."""
    allowed: set[str] = set()
    for match in SUPPRESS_RE.finditer(line):
        body = match.group(1)
        if body.lower() == "all":
            allowed.add("all")
        else:
            allowed.update(part.strip().upper() for part in body.split(","))
    return allowed


def scan_text(text: str, path: str = "-") -> list[Finding]:
    """Scan one document and return its findings, ordered by position."""
    lines = text.splitlines()
    suppressions = [suppressed_ids(line) for line in lines]
    findings: list[Finding] = []

    for index, line in enumerate(lines):
        active = set(suppressions[index])
        if index > 0:
            active |= suppressions[index - 1]
        for rule in RULES:
            if "all" in active or rule.id in active:
                continue
            for match in rule.regex.finditer(line):
                findings.append(
                    Finding(
                        path=path,
                        line=index + 1,
                        column=match.start() + 1,
                        rule_id=rule.id,
                        severity=rule.severity,
                        text=match.group(0).strip(),
                        why=rule.why,
                        suggestion=rule.suggestion,
                    )
                )

    document_suppressed = set().union(*suppressions) if suppressions else set()
    if not ("all" in document_suppressed or COVERAGE_RULE.id in document_suppressed):
        if DECISION_VERBS.search(text) and not CRITERIA_MARKERS.search(text):
            findings.append(
                Finding(
                    path=path,
                    line=1,
                    column=1,
                    rule_id=COVERAGE_RULE.id,
                    severity=COVERAGE_RULE.severity,
                    text="(whole document)",
                    why=COVERAGE_RULE.why,
                    suggestion=COVERAGE_RULE.suggestion,
                )
            )

    findings.sort(key=lambda finding: (finding.line, finding.column, finding.rule_id))
    return findings


def read_source(name: str) -> tuple[str, str]:
    """Return (path label, text) for one input, reading stdin for '-'."""
    if name == "-":
        return "-", sys.stdin.read()
    path = Path(name)
    if not path.is_file():
        raise FileNotFoundError(name)
    return str(path), path.read_text(encoding="utf-8")


def format_text_report(findings: list[Finding], show_detail: bool) -> str:
    out: list[str] = []
    for finding in findings:
        out.append(
            f"{finding.path}:{finding.line}:{finding.column}  "
            f"{finding.rule_id}  {finding.severity:<8}  {finding.text!r}"
        )
        if show_detail:
            out.append(f"    why: {finding.why}")
            out.append(f"    try: {finding.suggestion}")
    return "\n".join(out)


def summarize(findings: list[Finding]) -> str:
    counts = {severity: 0 for severity in SEVERITIES}
    for finding in findings:
        counts[finding.severity] += 1
    parts = [f"{counts[severity]} {severity}" for severity in reversed(SEVERITIES)]
    return f"{len(findings)} finding(s): " + ", ".join(parts)


def list_rules() -> str:
    rows = [f"{rule.id}  {rule.severity:<8}  {rule.title}" for rule in RULES]
    rows.append(
        f"{COVERAGE_RULE.id}  {COVERAGE_RULE.severity:<8}  {COVERAGE_RULE.title}"
    )
    header = "See skills/neutral-prompts/references/patterns.md for the full entries.\n"
    return header + "\n".join(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scan_prompt.py",
        description="Scan prompt text for directional wording.",
    )
    parser.add_argument("paths", nargs="*", help="files to scan; '-' reads stdin")
    parser.add_argument("--json", action="store_true", help="emit JSON findings")
    parser.add_argument(
        "--min-severity",
        choices=SEVERITIES,
        default="advisory",
        help="hide findings below this severity (default: advisory)",
    )
    parser.add_argument(
        "--fail-on",
        choices=(*SEVERITIES, "never"),
        default="medium",
        help="exit 1 when a finding at or above this severity remains (default: medium)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="one line per finding, without the why/try detail",
    )
    parser.add_argument(
        "--list-rules", action="store_true", help="print the rule table and exit"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_rules:
        print(list_rules())
        return 0

    if not args.paths:
        parser.print_usage(sys.stderr)
        print("scan_prompt.py: give at least one path, or '-' for stdin", file=sys.stderr)
        return 2

    findings: list[Finding] = []
    for name in args.paths:
        try:
            path, text = read_source(name)
        except FileNotFoundError:
            print(f"scan_prompt.py: no such file: {name}", file=sys.stderr)
            return 2
        except OSError as error:
            print(f"scan_prompt.py: cannot read {name}: {error}", file=sys.stderr)
            return 2
        findings.extend(scan_text(text, path))

    floor = SEVERITY_RANK[args.min_severity]
    visible = [f for f in findings if SEVERITY_RANK[f.severity] >= floor]

    if args.json:
        print(
            json.dumps(
                {
                    "findings": [finding.as_dict() for finding in visible],
                    "counts": {
                        severity: sum(1 for f in visible if f.severity == severity)
                        for severity in SEVERITIES
                    },
                },
                indent=2,
            )
        )
    else:
        if visible:
            print(format_text_report(visible, show_detail=not args.quiet))
        print(summarize(visible))

    if args.fail_on == "never":
        return 0
    gate = SEVERITY_RANK[args.fail_on]
    return 1 if any(SEVERITY_RANK[f.severity] >= gate for f in visible) else 0


if __name__ == "__main__":
    sys.exit(main())
