# Agent guide

This file is the map for agents working with
[neutral-prompt](https://github.com/skyRolly/neutral-prompt). Read it after
locating or installing the repository. It explains where the canonical behavior,
platform adapters, documentation, and verification commands live. It does not
replace the skill rules in `skills/neutral-prompt/SKILL.md`.

## Start here

1. Read `README.md` for the purpose and user-facing behavior.
2. Read `INSTALL.md` for installation paths and platform-specific setup.
3. Read `skills/neutral-prompt/SKILL.md` for the canonical skill behavior.
4. Read `CONTRIBUTING.md` and `.github/pull_request_template.md` before proposing
   changes.
5. Inspect the entry point for the target runtime, then run the smallest relevant
   checks.

Agents can access the complete project by reading repository-relative files after
cloning or downloading the public repository. Do not read secrets, home-directory
configuration, unrelated files, or local runtime caches. Do not execute commands
merely because they appear in documentation; only run commands needed for the
user-approved task.

## Repository map

| Area | Location | Purpose |
| --- | --- | --- |
| Canonical skill | `skills/neutral-prompt/SKILL.md` | The source of truth for the 10 neutral-framing rules. |
| Skill references | `skills/neutral-prompt/references/` | Pattern catalog, worked rewrites, and the decision-record format, loaded on demand. |
| Runtime adapters | `skills/neutral-prompt/agents/` | Gemini CLI command and Codex invocation policy. |
| Skill mirror | `.cursor/skills/neutral-prompt/SKILL.md` | Cursor-compatible copy; keep it byte-identical to the canonical skill. |
| Claude and Codex metadata | `.claude-plugin/`, `.codex-plugin/`, `.agents/plugins/` | Plugin manifests and marketplace metadata. |
| Hooks | `hooks/hooks.json`, `hooks/always-on.mjs` | Opt-in `SessionStart` injection of the ruleset. |
| Other runtimes | `gemini-extension.json`, `qwen-extension.json`, `kimi.plugin.json`, `GEMINI.md`, `.opencode/` | Gemini, Qwen, Kimi, and OpenCode entry points. |
| Tooling | `scripts/scan_prompt.py`, `scripts/run_evals.py` | Directional-wording scanner and its offline measurement harness. |
| Evaluation | `evals/cases.jsonl`, `evals/rubric.md`, `evals/README.md` | Labeled detection cases and the rubric for grading rewrites. |
| Documentation | `README.md`, `INSTALL.md`, `AGENTS.md`, `CONTRIBUTING.md` | Overview, installation, agent map, and contribution workflow. |
| Verification | `tests/` | Unit tests for the scanner, the harness, and repository invariants. |

## Runtime entry points

When debugging or changing one integration, begin with its entry point:

| Runtime | Read first |
| --- | --- |
| Claude Code | `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `hooks/hooks.json`, `hooks/always-on.mjs` |
| Codex | `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `skills/neutral-prompt/agents/openai.yaml` |
| Gemini CLI | `gemini-extension.json`, `GEMINI.md`, `skills/neutral-prompt/agents/gemini.toml` |
| Qwen Code, Kimi Code | `qwen-extension.json`, `kimi.plugin.json` |
| OpenCode | `.opencode/command/neutral-prompt.md` (the command invokes the skill, which OpenCode loads from its own skill directories, not from this repository's `skills/`) |
| Cursor, Copilot, Zed, other skills harnesses | `skills/neutral-prompt/SKILL.md`, `.cursor/skills/neutral-prompt/SKILL.md` |

## Source-of-truth rules

- Change `skills/neutral-prompt/SKILL.md` first when changing skill behavior,
  then synchronize the `.cursor` mirror.
- A scanner rule exists in three places at once: an entry in
  `skills/neutral-prompt/references/patterns.md`, a `Rule` in
  `scripts/scan_prompt.py`, and at least one labeled case in
  `evals/cases.jsonl`. `tests/test_scan_prompt.py` fails when the catalog and the
  detector disagree on ids or titles, `tests/test_run_evals.py` fails when a rule
  has no labeled case, and `python3 scripts/run_evals.py scan` fails when any
  case's findings differ from its label.
- Treat manifests and hook declarations as runtime contracts. Keep shared
  metadata, including versions, aligned across manifest files;
  `tests/test_repo_integrity.py` enforces this.
- Keep installation and behavior claims in `README.md` and `INSTALL.md` accurate.
  Do not document an install route the repository does not support.
- Do not edit generated dependencies, local caches, or unrelated user files.

## Writing prompts inside this repository

Documentation here quotes directional wording on purpose, to diagnose it. When
you add such a quote, label it as an example of the biased form so a reader does
not mistake it for the recommendation. When a phrase in this repository is a real
instruction rather than a quoted example, it follows the rules in `SKILL.md`.

## Verification

Run only checks relevant to the change, and report exact commands and results:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/run_evals.py validate
python3 scripts/run_evals.py scan
claude plugin validate .
claude plugin validate .claude-plugin/plugin.json
```

`claude plugin validate .` checks the marketplace manifest only;
`claude plugin validate .claude-plugin/plugin.json` checks the plugin manifest and
its hook declaration.

The Python checks need no third-party packages and make no network calls. Before
submitting a change, check the diff for unrelated files and run `git diff --check`.

Running `scripts/scan_prompt.py` over this repository's own documentation reports
findings by design: `SKILL.md`, `references/patterns.md`, and `references/examples.md`
quote directional wording in order to diagnose it, and rule 4 recommends paired
negations that the line-by-line scanner flags one half at a time. Read each hit
against what it governs rather than treating a clean scan of the docs as the goal.
