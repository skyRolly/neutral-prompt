import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_evals  # noqa: E402

VALID_CASE = {
    "id": "sample",
    "category": "lifecycle",
    "kind": "directional",
    "text": "Do not stop them.",
    "expect": ["NP001", "NP012"],
    "note": "A negation that installs continuation as the default.",
}


def write_cases(directory, cases):
    path = Path(directory) / "cases.jsonl"
    path.write_text(
        "\n".join(json.dumps(case) for case in cases) + "\n", encoding="utf-8"
    )
    return path


class CaseFileTest(unittest.TestCase):
    def test_shipped_cases_are_valid(self):
        cases = run_evals.load_cases(run_evals.CASES_PATH)
        self.assertEqual(run_evals.validate_cases(cases), [])
        self.assertGreaterEqual(len(cases), 20)

    def test_shipped_cases_all_match(self):
        cases = run_evals.load_cases(run_evals.CASES_PATH)
        report = run_evals.evaluate(cases)
        self.assertEqual(report["mismatched"], [])

    def test_shipped_cases_cover_every_rule(self):
        cases = run_evals.load_cases(run_evals.CASES_PATH)
        report = run_evals.evaluate(cases)
        self.assertEqual(run_evals.rules_without_coverage(report["per_rule"]), [])

    def test_shipped_cases_include_both_kinds(self):
        cases = run_evals.load_cases(run_evals.CASES_PATH)
        kinds = {case["kind"] for case in cases}
        self.assertEqual(kinds, {"directional", "neutral"})

    def test_invalid_json_is_reported_with_a_line_number(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cases.jsonl"
            path.write_text('{"id": "ok"}\nnot json\n', encoding="utf-8")
            with self.assertRaises(ValueError) as raised:
                run_evals.load_cases(path)
            self.assertIn(":2:", str(raised.exception))

    def test_blank_lines_are_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_cases(tmp, [VALID_CASE])
            path.write_text(path.read_text() + "\n\n", encoding="utf-8")
            self.assertEqual(len(run_evals.load_cases(path)), 1)


class ValidationTest(unittest.TestCase):
    def problems_for(self, **overrides):
        case = dict(VALID_CASE)
        case.update(overrides)
        return run_evals.validate_cases([case])

    def test_valid_case_has_no_problems(self):
        self.assertEqual(self.problems_for(), [])

    def test_missing_field(self):
        case = dict(VALID_CASE)
        del case["note"]
        problems = run_evals.validate_cases([case])
        self.assertTrue(any("missing field" in problem for problem in problems))

    def test_unknown_rule_id(self):
        problems = self.problems_for(expect=["NP999"])
        self.assertTrue(any("unknown rule id" in problem for problem in problems))

    def test_duplicate_rule_id(self):
        problems = self.problems_for(expect=["NP001", "NP001"])
        self.assertTrue(any("duplicate rule ids" in problem for problem in problems))

    def test_bad_kind(self):
        problems = self.problems_for(kind="biased")
        self.assertTrue(any("kind must be" in problem for problem in problems))

    def test_bad_category(self):
        problems = self.problems_for(category="lifecyle")
        self.assertTrue(any("category must be" in problem for problem in problems))

    def test_directional_case_needs_an_expectation(self):
        problems = self.problems_for(expect=[])
        self.assertTrue(any("at least one rule" in problem for problem in problems))

    def test_neutral_case_may_expect_nothing(self):
        problems = self.problems_for(
            kind="neutral", text="Summarize the file.", expect=[]
        )
        self.assertEqual(problems, [])

    def test_duplicate_ids_across_cases(self):
        problems = run_evals.validate_cases([dict(VALID_CASE), dict(VALID_CASE)])
        self.assertTrue(any("duplicate id" in problem for problem in problems))

    def test_empty_text(self):
        problems = self.problems_for(text="   ")
        self.assertTrue(any("non-empty string" in problem for problem in problems))

    def test_empty_note(self):
        problems = self.problems_for(note="")
        self.assertTrue(any("note must explain" in problem for problem in problems))


class EvaluateTest(unittest.TestCase):
    def test_mismatch_is_reported_in_both_directions(self):
        case = dict(VALID_CASE, expect=["NP003", "NP012"])
        report = run_evals.evaluate([case])
        result = report["results"][0]
        self.assertEqual(result["missed"], ["NP003"])
        self.assertEqual(result["extra"], ["NP001"])
        self.assertFalse(result["matched"])

    def test_known_limitation_flagged_for_neutral_case_with_expectations(self):
        case = dict(
            VALID_CASE,
            kind="neutral",
            text="Do not stop the workflow by default. Do not continue it by default.",
            expect=["NP001"],
        )
        report = run_evals.evaluate([case])
        self.assertEqual(len(report["known_limitations"]), 1)


class CommandLineTest(unittest.TestCase):
    def run_cli(self, args):
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "run_evals.py"), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_validate_passes_on_shipped_cases(self):
        result = self.run_cli(["validate"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("valid", result.stdout)

    def test_scan_passes_on_shipped_cases(self):
        result = self.run_cli(["scan"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("all cases matched", result.stdout)

    def test_scan_json_payload(self):
        result = self.run_cli(["scan", "--json"])
        payload = json.loads(result.stdout)
        self.assertEqual(payload["cases"], payload["matched"])
        self.assertEqual(payload["mismatched"], [])

    def test_mismatch_exits_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_cases(tmp, [dict(VALID_CASE, expect=["NP009"])])
            result = self.run_cli(["scan", "--cases", str(path)])
            self.assertEqual(result.returncode, 1)
            self.assertIn("mismatched cases", result.stdout)

    def test_invalid_case_file_exits_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_cases(tmp, [dict(VALID_CASE, expect=["NP999"])])
            result = self.run_cli(["validate", "--cases", str(path)])
            self.assertEqual(result.returncode, 1)
            self.assertIn("unknown rule id", result.stderr)

    def test_directory_exits_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_cli(["validate", "--cases", tmp])
            self.assertEqual(result.returncode, 2)
            self.assertIn("cannot read", result.stderr)

    def test_missing_case_file_exits_two(self):
        result = self.run_cli(["validate", "--cases", "nope.jsonl"])
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
