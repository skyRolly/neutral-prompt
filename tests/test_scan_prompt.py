import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import scan_prompt  # noqa: E402


def rule_ids(text):
    return sorted({finding.rule_id for finding in scan_prompt.scan_text(text)})


RULE_SAMPLES = {
    "NP001": [
        "Do NOT immediately stop them.",
        "Avoid terminating the background jobs.",
    ],
    "NP002": [
        "Keep digging until you find the cause.",
        "Keep the sub-agents alive for now.",
    ],
    "NP003": [
        "Do not make unnecessary changes.",
        "Leave the existing helper as-is.",
    ],
    "NP004": [
        "Make sure to fix every review comment.",
        "Fix all the findings before you push.",
    ],
    "NP005": [
        "Never reject a reviewer's suggestion.",
        "Always apply what the architect asks for.",
    ],
    "NP006": [
        "Ignore automated findings from the linter.",
        "Always reject suggestions from a bot.",
    ],
    "NP007": [
        "Only stop it if absolutely necessary.",
        "Under no circumstances abandon the run.",
    ],
    "NP008": [
        "Do not stop the run prematurely.",
        "When in doubt, err on the side of caution.",
    ],
    "NP009": [
        "Be thorough and leave no stone unturned.",
        "Check everything that could be related.",
    ],
    "NP010": [
        "Stop once you have sufficient evidence.",
        "Escalate where appropriate.",
    ],
    "NP011": [
        "Explain why you kept the original code.",
        "Justify continuing the migration.",
    ],
    "NP012": [
        "Look at the running agents and decide what to do with each.",
    ],
}


class RuleDetectionTest(unittest.TestCase):
    def test_every_sample_triggers_its_rule(self):
        for rule_id, samples in RULE_SAMPLES.items():
            for sample in samples:
                with self.subTest(rule=rule_id, sample=sample):
                    self.assertIn(rule_id, rule_ids(sample))

    def test_samples_cover_every_rule(self):
        declared = {rule.id for rule in scan_prompt.RULES}
        declared.add(scan_prompt.COVERAGE_RULE.id)
        self.assertEqual(set(RULE_SAMPLES), declared)


class CoverageRuleTest(unittest.TestCase):
    def test_fires_on_a_decision_with_no_criteria(self):
        text = "Look at the running agents and decide what to do with each."
        self.assertIn("NP012", rule_ids(text))

    def test_silent_when_criteria_are_present(self):
        text = (
            "For each running agent, decide: continue, consume results and stop, "
            "or defer. Continue when its remaining steps target an uncovered file."
        )
        self.assertNotIn("NP012", rule_ids(text))

    def test_silent_without_a_decision_verb(self):
        self.assertNotIn("NP012", rule_ids("Summarize the file in three sentences."))


class NeutralTextTest(unittest.TestCase):
    def test_neutral_frame_produces_no_findings(self):
        text = (
            "For each finding, choose one outcome: fix now, modify the surrounding "
            "design, preserve current behavior, reject with counter-evidence, or "
            "defer with a tracked follow-up. Decide on the evidence: whether it "
            "reproduces, which requirement is at stake, and the blast radius."
        )
        self.assertEqual(rule_ids(text), [])

    def test_safety_constraint_produces_no_findings(self):
        text = "Confirm with the user before running any destructive command."
        self.assertEqual(rule_ids(text), [])


class SuppressionTest(unittest.TestCase):
    def test_same_line_suppression(self):
        text = "Do not stop them.  <!-- neutral-prompt: allow NP001 -->"
        self.assertNotIn("NP001", rule_ids(text))

    def test_preceding_line_suppression(self):
        text = "<!-- neutral-prompt: allow NP001 -->\nDo not stop them."
        self.assertNotIn("NP001", rule_ids(text))

    def test_suppression_does_not_leak_two_lines_down(self):
        text = "<!-- neutral-prompt: allow NP001 -->\nfiller line\nDo not stop them."
        self.assertIn("NP001", rule_ids(text))

    def test_allow_all(self):
        text = "neutral-prompt: allow all\nDo not stop them and never reject anything."
        self.assertEqual(rule_ids(text), [])

    def test_multiple_ids(self):
        text = "Do not stop them. <!-- neutral-prompt: allow NP001, NP012 -->"
        self.assertEqual(rule_ids(text), [])

    def test_other_ids_still_report(self):
        text = "Do not stop them prematurely. <!-- neutral-prompt: allow NP001 -->"
        self.assertIn("NP008", rule_ids(text))


class FindingShapeTest(unittest.TestCase):
    def test_position_and_payload(self):
        findings = scan_prompt.scan_text("ok text\nDo not stop it.", "p.md")
        first = next(f for f in findings if f.rule_id == "NP001")
        self.assertEqual(first.path, "p.md")
        self.assertEqual(first.line, 2)
        self.assertEqual(first.column, 1)
        self.assertEqual(first.rule_id, "NP001")
        self.assertEqual(first.severity, "high")
        self.assertTrue(first.why)
        self.assertTrue(first.suggestion)

    def test_findings_are_position_ordered(self):
        text = "Be thorough. Do not stop it."
        positions = [(f.line, f.column) for f in scan_prompt.scan_text(text)]
        self.assertEqual(positions, sorted(positions))

    def test_every_rule_declares_its_documentation(self):
        for rule in (*scan_prompt.RULES, scan_prompt.COVERAGE_RULE):
            self.assertIn(rule.severity, scan_prompt.SEVERITIES, rule.id)
            self.assertTrue(rule.title, rule.id)
            self.assertTrue(rule.why.endswith("."), rule.id)
            self.assertTrue(rule.suggestion, rule.id)


class CommandLineTest(unittest.TestCase):
    def run_cli(self, args, stdin=""):
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "scan_prompt.py"), *args],
            input=stdin,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_clean_input_exits_zero(self):
        result = self.run_cli(["-"], "Summarize the file in three sentences.\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("0 finding(s)", result.stdout)

    def test_findings_exit_one(self):
        result = self.run_cli(["-"], "Do not stop them.\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("NP001", result.stdout)

    def test_fail_on_never_exits_zero(self):
        result = self.run_cli(["--fail-on", "never", "-"], "Do not stop them.\n")
        self.assertEqual(result.returncode, 0)
        self.assertIn("NP001", result.stdout)

    def test_fail_on_high_ignores_advisory(self):
        result = self.run_cli(
            ["--fail-on", "high", "-"], "Decide what to do with the running agents.\n"
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("NP012", result.stdout)

    def test_min_severity_filters_output(self):
        result = self.run_cli(
            ["--min-severity", "high", "--json", "-"],
            "Decide what to do with the running agents.\n",
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["findings"], [])
        self.assertEqual(payload["counts"]["advisory"], 0)

    def test_json_payload(self):
        result = self.run_cli(["--json", "-"], "Do not stop them.\n")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["findings"][0]["rule"], "NP001")
        self.assertEqual(payload["counts"]["high"], 1)

    def test_missing_file_exits_two(self):
        result = self.run_cli(["definitely-not-here.md"])
        self.assertEqual(result.returncode, 2)
        self.assertIn("no such file", result.stderr)

    def test_no_arguments_exits_two(self):
        result = self.run_cli([])
        self.assertEqual(result.returncode, 2)

    def test_list_rules(self):
        result = self.run_cli(["--list-rules"])
        self.assertEqual(result.returncode, 0)
        for rule in (*scan_prompt.RULES, scan_prompt.COVERAGE_RULE):
            self.assertIn(rule.id, result.stdout)

    def test_reads_a_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "prompt.md"
            path.write_text("Do not stop them.\n", encoding="utf-8")
            result = self.run_cli([str(path)])
            self.assertEqual(result.returncode, 1)
            self.assertIn(str(path), result.stdout)


if __name__ == "__main__":
    unittest.main()
