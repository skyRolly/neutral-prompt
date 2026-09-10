import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "neutral-prompt"
SKILL_DIR = ROOT / "skills" / SKILL_NAME
SKILL_PATH = SKILL_DIR / "SKILL.md"
MIRROR_PATH = ROOT / ".cursor" / "skills" / SKILL_NAME / "SKILL.md"

VERSIONED_MANIFESTS = (
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    "gemini-extension.json",
    "qwen-extension.json",
    "kimi.plugin.json",
)
NAMED_MANIFESTS = VERSIONED_MANIFESTS + (
    ".claude-plugin/marketplace.json",
    ".agents/plugins/marketplace.json",
)

PLACEHOLDER_RE = re.compile(
    r"\b(?:TODO|TBD|FIXME|XXX|lorem ipsum|coming soon|placeholder)\b", re.IGNORECASE
)
SKILL_PATH_RE = re.compile(r"skills/([\w.-]+)/SKILL\.md")
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".toml", ".py", ".mjs", ".jsonl"}


def tracked_files():
    """Every git-tracked file, so scratch and ignored files stay out of the checks."""
    output = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [ROOT / line for line in output.splitlines() if line]


def tracked_text_files():
    return [path for path in tracked_files() if path.suffix in TEXT_SUFFIXES]


def frontmatter(text):
    """Parse the leading YAML block far enough to read its scalar keys."""
    match = re.match(r"^---[^\S\r\n]*\r?\n(.*?)\r?\n---[^\S\r\n]*(?:\r?\n|$)", text, re.S)
    if not match:
        return {}
    fields = {}
    for line in match.group(1).splitlines():
        if line.startswith((" ", "\t")) or ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip("'\"")
    return fields


class SkillFileTest(unittest.TestCase):
    def setUp(self):
        self.text = SKILL_PATH.read_text(encoding="utf-8")
        self.fields = frontmatter(self.text)

    def test_skill_exists(self):
        self.assertTrue(SKILL_PATH.is_file())

    def test_frontmatter_name_matches_directory(self):
        self.assertEqual(self.fields.get("name"), SKILL_NAME)
        self.assertEqual(SKILL_DIR.name, SKILL_NAME)

    def test_frontmatter_declares_a_description(self):
        description = self.fields.get("description", "")
        self.assertGreater(len(description), 80)
        self.assertLess(len(description), 1024)

    def test_activation_is_explicit(self):
        self.assertEqual(self.fields.get("disable-model-invocation"), "true")

    def test_declares_the_licence_it_ships_under(self):
        self.assertEqual(self.fields.get("license"), "MIT")

    def test_names_every_admissible_outcome(self):
        for outcome in (
            "proceed",
            "stop",
            "modify",
            "preserve",
            "accept",
            "reject",
            "defer",
        ):
            self.assertIn(outcome, self.text.lower(), outcome)

    def test_names_the_four_decision_steps(self):
        for step in ("Gather", "Evaluate", "Choose", "Record"):
            self.assertIn(step, self.text, step)


class MirrorTest(unittest.TestCase):
    def test_cursor_mirror_is_byte_identical(self):
        self.assertEqual(
            MIRROR_PATH.read_bytes(),
            SKILL_PATH.read_bytes(),
            "run: cp skills/neutral-prompt/SKILL.md .cursor/skills/neutral-prompt/SKILL.md",
        )

    def test_mirror_is_a_real_file_not_a_symlink(self):
        self.assertFalse(MIRROR_PATH.is_symlink())


class ManifestTest(unittest.TestCase):
    def load(self, relative):
        return json.loads((ROOT / relative).read_text(encoding="utf-8"))

    def test_every_json_file_parses(self):
        for path in tracked_files():
            if path.suffix == ".json":
                with self.subTest(path=str(path.relative_to(ROOT))):
                    json.loads(path.read_text(encoding="utf-8"))

    def test_manifests_agree_on_the_name(self):
        for relative in NAMED_MANIFESTS:
            with self.subTest(manifest=relative):
                self.assertEqual(self.load(relative)["name"], SKILL_NAME)

    def test_manifests_agree_on_the_version(self):
        versions = {self.load(r)["version"] for r in VERSIONED_MANIFESTS}
        self.assertEqual(len(versions), 1, f"versions differ: {sorted(versions)}")

    def test_manifests_describe_themselves(self):
        # .agents/plugins/marketplace.json carries its copy under interface/plugins,
        # so only the manifests with a top-level description are checked here.
        for relative in VERSIONED_MANIFESTS + (".claude-plugin/marketplace.json",):
            with self.subTest(manifest=relative):
                self.assertGreater(len(self.load(relative)["description"]), 40)

    def test_marketplace_plugin_entry_matches(self):
        entries = self.load(".claude-plugin/marketplace.json")["plugins"]
        self.assertEqual([entry["name"] for entry in entries], [SKILL_NAME])


class ReferenceTest(unittest.TestCase):
    def test_every_reference_file_is_linked_from_the_skill(self):
        text = SKILL_PATH.read_text(encoding="utf-8")
        for path in sorted((SKILL_DIR / "references").glob("*.md")):
            with self.subTest(reference=path.name):
                self.assertIn(f"references/{path.name}", text)

    def test_every_skill_path_mentioned_anywhere_exists(self):
        for path in tracked_text_files():
            for slug in set(SKILL_PATH_RE.findall(path.read_text(encoding="utf-8"))):
                with self.subTest(path=str(path.relative_to(ROOT)), slug=slug):
                    self.assertTrue(
                        (ROOT / "skills" / slug / "SKILL.md").is_file(),
                        f"{path.relative_to(ROOT)} points at a skill that does not exist",
                    )

    def test_only_one_skill_ships(self):
        skills = sorted(p.name for p in (ROOT / "skills").iterdir() if p.is_dir())
        self.assertEqual(skills, [SKILL_NAME])

    def test_no_placeholder_content(self):
        for path in tracked_text_files():
            if path.name == "test_repo_integrity.py":
                continue  # this file names the markers it searches for
            text = path.read_text(encoding="utf-8")
            for number, line in enumerate(text.splitlines(), 1):
                with self.subTest(path=str(path.relative_to(ROOT)), line=number):
                    self.assertIsNone(
                        PLACEHOLDER_RE.search(line), f"placeholder marker: {line.strip()}"
                    )


class AlwaysOnHookTest(unittest.TestCase):
    """The SessionStart hook is opt-in and must never block a session."""

    def setUp(self):
        self.node = shutil.which("node")
        if not self.node:
            self.skipTest("node is not installed")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        # A path with a space catches quoting mistakes in the hook declaration.
        self.plugin_root = Path(self.temp.name) / "plugin root"
        shutil.copytree(ROOT / "hooks", self.plugin_root / "hooks")
        shutil.copytree(ROOT / "skills", self.plugin_root / "skills")
        self.config_dir = Path(self.temp.name) / "claude config"
        self.config_dir.mkdir()

    def run_hook(self):
        env = os.environ.copy()
        env["CLAUDE_CONFIG_DIR"] = str(self.config_dir)
        return subprocess.run(
            [self.node, str(self.plugin_root / "hooks" / "always-on.mjs")],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )

    def set_flag(self):
        (self.config_dir / ".neutral-prompt-always").write_text("", encoding="utf-8")

    def test_silent_without_the_flag(self):
        result = self.run_hook()
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_emits_the_ruleset_with_the_flag(self):
        self.set_flag()
        result = self.run_hook()
        self.assertEqual(result.returncode, 0)
        self.assertIn("NEUTRAL PROMPT MODE ACTIVE", result.stdout)
        self.assertIn("Separate settled constraints from open decisions", result.stdout)

    def test_strips_the_frontmatter(self):
        self.set_flag()
        result = self.run_hook()
        self.assertNotIn("disable-model-invocation", result.stdout)

    def test_names_the_off_switch_and_the_flag_path(self):
        self.set_flag()
        result = self.run_hook()
        self.assertIn("stop neutral mode", result.stdout)
        self.assertIn(str(self.config_dir / ".neutral-prompt-always"), result.stdout)

    def test_exits_zero_when_the_skill_is_missing(self):
        self.set_flag()
        shutil.rmtree(self.plugin_root / "skills")
        result = self.run_hook()
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_hook_declaration_points_at_the_shipped_script(self):
        declaration = json.loads((ROOT / "hooks" / "hooks.json").read_text())
        entries = declaration["hooks"]["SessionStart"]
        commands = [hook["command"] for entry in entries for hook in entry["hooks"]]
        self.assertTrue(any("always-on.mjs" in command for command in commands))


if __name__ == "__main__":
    unittest.main()
