# How to install

<details>
<summary><strong>Claude Code</strong></summary>

### Install

```bash
claude plugin marketplace add skyRolly/neutral-prompt
claude plugin install neutral-prompt@neutral-prompt
```

Type `/neutral-prompt`.

### Verify

```bash
claude plugin list
```

### Update

```bash
claude plugin marketplace update neutral-prompt
```

### Uninstall

```bash
claude plugin uninstall neutral-prompt
claude plugin marketplace remove neutral-prompt
```

Or keep it installed and turn it off: `claude plugin disable neutral-prompt`.

### Always-on (optional)

A `SessionStart` hook loads the full ruleset at the start of every session, no
`/neutral-prompt` needed:

```bash
touch ~/.claude/.neutral-prompt-always
```

If you use a custom Claude configuration directory, create the flag there instead:

```bash
touch "$CLAUDE_CONFIG_DIR/.neutral-prompt-always"
```

Back to on-demand:

```bash
rm ~/.claude/.neutral-prompt-always
```

The hook only fires when the flag file exists, so installing the plugin changes
nothing by itself. "stop neutral mode" still turns it off for the current session.

</details>

<details>
<summary><strong>Codex</strong></summary>

### Install

```bash
codex plugin marketplace add skyRolly/neutral-prompt --ref main
codex plugin add neutral-prompt@neutral-prompt
```

Invoke the skill explicitly by typing `$neutral-prompt`. Codex will not activate
it automatically: `skills/neutral-prompt/agents/openai.yaml` sets
`policy.allow_implicit_invocation: false`.

### Verify

```bash
codex plugin list
```

### Update

```bash
codex plugin marketplace upgrade neutral-prompt
codex plugin remove neutral-prompt
codex plugin add neutral-prompt@neutral-prompt
```

### Uninstall

```bash
codex plugin remove neutral-prompt
codex plugin marketplace remove neutral-prompt
```

### Always-on (optional)

Add to `~/.codex/AGENTS.md`:

```markdown
## Prompt framing

Apply these rules to every prompt you write, review, or rewrite. They govern open
decisions — the choices a prompt delegates — not settled constraints such as
safety rules, output contracts, budgets, or coding standards.

1. Separate settled constraints from open decisions; write constraints as imperatives.
2. Name the decision, not the answer.
3. List every admissible outcome: proceed, stop, modify, preserve, accept, reject, defer.
4. Balance the negations — ruling out one default installs its opposite.
5. Replace protected actions ("do not stop", "avoid changing", "always fix") with the criterion they were hiding.
6. Order the prompt: gather evidence, evaluate alternatives, choose an action, record the reasoning.
7. Keep the intensity symmetric across outcomes; "must continue" against "may stop" is a ranking.
8. Make thresholds observable — replace "enough", "sufficient", "significant", "as needed", "premature".
9. Require the decision record, not a particular decision.
10. Do not manufacture balance: state the evidence you hold, withhold only the conclusion.

Directive wording is correct when the author has already decided, when safety or
legality is at stake, when an external contract dictates the outcome, when an
outcome is genuinely inadmissible and named as such, or when the decision is small
enough that one balanced sentence carries the whole frame.
```

</details>

<details>
<summary><strong>Gemini CLI</strong></summary>

Gemini CLI has no plugin marketplace, so there are two native routes: a **custom
command** (opt-in, off until you invoke it) or an **extension** (always-on once
installed). The command route matches this skill's default posture; pick it unless
you want the rules on every session.

### Install (command, opt-in)

```bash
mkdir -p ~/.gemini/commands
curl -fsSL https://raw.githubusercontent.com/skyRolly/neutral-prompt/main/skills/neutral-prompt/agents/gemini.toml \
  -o ~/.gemini/commands/neutral-prompt.toml
```

Start a new session, type `/neutral-prompt`. It stays on for that session.

### Install (extension, always-on)

```bash
gemini extensions install https://github.com/skyRolly/neutral-prompt
```

The extension loads `GEMINI.md`, which imports the full skill, so the rules apply
from message one. `git` must be installed.

### Verify

```bash
gemini extensions list          # extension route
ls ~/.gemini/commands           # command route: neutral-prompt.toml present
```

Or type `/` in a session and confirm `neutral-prompt` is listed.

### Update

```bash
gemini extensions update neutral-prompt    # extension route
# command route: re-run the curl above
```

### Uninstall

```bash
gemini extensions uninstall neutral-prompt    # extension route
rm ~/.gemini/commands/neutral-prompt.toml     # command route
```

</details>

<details>
<summary><strong>GitHub Copilot (VS Code and Copilot CLI)</strong></summary>

Copilot reads Agent Skills natively: the same `SKILL.md`, no conversion. It scans
`.github/skills/`, `.claude/skills/`, and `.agents/skills/` in the project, and
`~/.copilot/skills/`, `~/.claude/skills/`, and `~/.agents/skills/` globally.

### Install

```bash
npx skills add skyRolly/neutral-prompt -a github-copilot        # this project
npx skills add skyRolly/neutral-prompt -a github-copilot -g     # all projects
```

Without the CLI, copy the skill folder into any directory Copilot scans:

```bash
git clone https://github.com/skyRolly/neutral-prompt
mkdir -p ~/.copilot/skills
cp -R neutral-prompt/skills/neutral-prompt ~/.copilot/skills/
```

### Verify

Type `/` in the chat input and confirm `neutral-prompt` appears. Or:

```bash
npx skills list
npx skills ls -g    # if installed globally
```

### Update

```bash
npx skills update neutral-prompt
```

Or re-copy the folder after `git pull`.

### Uninstall

```bash
npx skills remove neutral-prompt
```

### Always-on (optional)

Add the block below to `.github/copilot-instructions.md` in the project:

```markdown
## Prompt framing

Apply these rules to every prompt you write, review, or rewrite. They govern open
decisions — the choices a prompt delegates — not settled constraints such as
safety rules, output contracts, budgets, or coding standards.

1. Separate settled constraints from open decisions; write constraints as imperatives.
2. Name the decision, not the answer.
3. List every admissible outcome: proceed, stop, modify, preserve, accept, reject, defer.
4. Balance the negations — ruling out one default installs its opposite.
5. Replace protected actions ("do not stop", "avoid changing", "always fix") with the criterion they were hiding.
6. Order the prompt: gather evidence, evaluate alternatives, choose an action, record the reasoning.
7. Keep the intensity symmetric across outcomes; "must continue" against "may stop" is a ranking.
8. Make thresholds observable — replace "enough", "sufficient", "significant", "as needed", "premature".
9. Require the decision record, not a particular decision.
10. Do not manufacture balance: state the evidence you hold, withhold only the conclusion.

Directive wording is correct when the author has already decided, when safety or
legality is at stake, when an external contract dictates the outcome, when an
outcome is genuinely inadmissible and named as such, or when the decision is small
enough that one balanced sentence carries the whole frame.
```

</details>

<details>
<summary><strong>Kimi Code CLI</strong></summary>

### Install

Start a Kimi Code session, then:

1. Run `/plugins`.
2. Choose **Custom**.
3. Paste `https://github.com/skyRolly/neutral-prompt` and press `Enter`.
4. Choose **Trust and install**.

Use the slash command `/skill:neutral-prompt` to invoke the skill explicitly.

### Update

`/plugins` in a Kimi Code session, cursor to **Neutral Prompts**, press `R`.

### Uninstall

`/plugins` in a Kimi Code session, cursor to **Neutral Prompts**, press `D`.

</details>

<details>
<summary><strong>OpenCode</strong></summary>

OpenCode reads `skills/` natively, so the skill works from any directory OpenCode
scans. The repository also ships `.opencode/command/neutral-prompt.md`, which adds
a `/neutral-prompt` command to a project that has it.

### Install

```bash
npx skills add skyRolly/neutral-prompt -a opencode -y
```

Or copy both pieces by hand:

```bash
git clone https://github.com/skyRolly/neutral-prompt
mkdir -p ~/.config/opencode/skills ~/.config/opencode/command
cp -R neutral-prompt/skills/neutral-prompt ~/.config/opencode/skills/
cp neutral-prompt/.opencode/command/neutral-prompt.md ~/.config/opencode/command/
```

### Verify

Start OpenCode, type `/`, and confirm `neutral-prompt` appears.

### Update

```bash
npx skills update neutral-prompt
```

Or re-copy after `git pull`.

### Uninstall

Delete `neutral-prompt` from the skills directory it landed in, and remove
`command/neutral-prompt.md`.

### Always-on (optional)

Add to `~/.config/opencode/AGENTS.md`:

```markdown
## Prompt framing

Apply these rules to every prompt you write, review, or rewrite. They govern open
decisions — the choices a prompt delegates — not settled constraints such as
safety rules, output contracts, budgets, or coding standards.

1. Separate settled constraints from open decisions; write constraints as imperatives.
2. Name the decision, not the answer.
3. List every admissible outcome: proceed, stop, modify, preserve, accept, reject, defer.
4. Balance the negations — ruling out one default installs its opposite.
5. Replace protected actions ("do not stop", "avoid changing", "always fix") with the criterion they were hiding.
6. Order the prompt: gather evidence, evaluate alternatives, choose an action, record the reasoning.
7. Keep the intensity symmetric across outcomes; "must continue" against "may stop" is a ranking.
8. Make thresholds observable — replace "enough", "sufficient", "significant", "as needed", "premature".
9. Require the decision record, not a particular decision.
10. Do not manufacture balance: state the evidence you hold, withhold only the conclusion.

Directive wording is correct when the author has already decided, when safety or
legality is at stake, when an external contract dictates the outcome, when an
outcome is genuinely inadmissible and named as such, or when the decision is small
enough that one balanced sentence carries the whole frame.
```

</details>

<details>
<summary><strong>Qwen Code</strong></summary>

### Install

```bash
qwen extensions install skyRolly/neutral-prompt
```

Qwen Code supports the GitHub shorthand and installs the repository as a native
extension. The extension discovers the skill under `skills/`.

Type `/neutral-prompt` to invoke the skill explicitly. Installing the extension
does not change behavior until the skill is invoked.

### Verify

```bash
qwen extensions list
```

Then start a new Qwen Code session and run:

```text
/skills
```

Confirm that `neutral-prompt` appears in the list.

### Update

```bash
qwen extensions update neutral-prompt
```

### Uninstall

```bash
qwen extensions uninstall neutral-prompt
```

</details>

<details>
<summary><strong>Zed</strong></summary>

Zed's Agent reads Agent Skills natively: the same `SKILL.md`, no conversion.

### Install

In the Agent Panel, open the Skills manager and choose **Create skill from URL**
(also in the command palette as `agent: create skill from url`), then paste:

```
https://github.com/skyRolly/neutral-prompt/blob/main/skills/neutral-prompt/SKILL.md
```

Save it in **User** scope for every project, or **Project** scope for one. Then
type `/neutral-prompt` in the Agent Panel.

Prefer the filesystem? Clone the repo and drop the skill folder into your user
skills directory:

```bash
git clone https://github.com/skyRolly/neutral-prompt
cp -R neutral-prompt/skills/neutral-prompt ~/.config/zed/skills/
```

### Verify

Open the Skills manager in the Agent Panel and confirm `neutral-prompt` is
listed. Or type `/` and confirm it appears.

### Update

Re-import from the same URL (overwrites), or re-copy the folder after `git pull`.

### Uninstall

Remove `neutral-prompt` from the Skills manager, or delete
`~/.config/zed/skills/neutral-prompt`.

### Always-on (optional)

Add to your personal `~/.config/zed/AGENTS.md`:

```markdown
## Prompt framing

Apply these rules to every prompt you write, review, or rewrite. They govern open
decisions — the choices a prompt delegates — not settled constraints such as
safety rules, output contracts, budgets, or coding standards.

1. Separate settled constraints from open decisions; write constraints as imperatives.
2. Name the decision, not the answer.
3. List every admissible outcome: proceed, stop, modify, preserve, accept, reject, defer.
4. Balance the negations — ruling out one default installs its opposite.
5. Replace protected actions ("do not stop", "avoid changing", "always fix") with the criterion they were hiding.
6. Order the prompt: gather evidence, evaluate alternatives, choose an action, record the reasoning.
7. Keep the intensity symmetric across outcomes; "must continue" against "may stop" is a ranking.
8. Make thresholds observable — replace "enough", "sufficient", "significant", "as needed", "premature".
9. Require the decision record, not a particular decision.
10. Do not manufacture balance: state the evidence you hold, withhold only the conclusion.

Directive wording is correct when the author has already decided, when safety or
legality is at stake, when an external contract dictates the outcome, when an
outcome is genuinely inadmissible and named as such, or when the decision is small
enough that one balanced sentence carries the whole frame.
```

</details>

<details>
<summary><strong>Cursor, Amp, and any other agent-skills harness</strong></summary>

Works with any harness that reads agent skills. Swap `-a <agent>` for yours.

### Install

```bash
npx skills add skyRolly/neutral-prompt                  # this workspace
npx skills add skyRolly/neutral-prompt -g               # all projects
npx skills add skyRolly/neutral-prompt -a cursor -y     # one agent only
```

New agent chat, type `/neutral-prompt`.

Without the CLI, copy the skill folder into whatever path your agent scans:

```bash
git clone https://github.com/skyRolly/neutral-prompt
mkdir -p ~/.cursor/skills     # Cursor. Use .agents/skills for OpenCode, or your agent's own path
cp -R neutral-prompt/skills/neutral-prompt ~/.cursor/skills/
```

### Verify

```bash
npx skills list
npx skills ls -g    # if installed globally
```

### Update

```bash
npx skills update neutral-prompt
npx skills update -g    # if installed globally
```

### Uninstall

```bash
npx skills remove neutral-prompt
npx skills remove neutral-prompt -g    # if installed globally
```

### Always-on (optional)

Paste this into your agent's persistent rules file. Cursor: **Settings → Rules →
User Rules**, or a project rule under `.cursor/rules/` with `alwaysApply: true`.

```markdown
## Prompt framing

Apply these rules to every prompt you write, review, or rewrite. They govern open
decisions — the choices a prompt delegates — not settled constraints such as
safety rules, output contracts, budgets, or coding standards.

1. Separate settled constraints from open decisions; write constraints as imperatives.
2. Name the decision, not the answer.
3. List every admissible outcome: proceed, stop, modify, preserve, accept, reject, defer.
4. Balance the negations — ruling out one default installs its opposite.
5. Replace protected actions ("do not stop", "avoid changing", "always fix") with the criterion they were hiding.
6. Order the prompt: gather evidence, evaluate alternatives, choose an action, record the reasoning.
7. Keep the intensity symmetric across outcomes; "must continue" against "may stop" is a ranking.
8. Make thresholds observable — replace "enough", "sufficient", "significant", "as needed", "premature".
9. Require the decision record, not a particular decision.
10. Do not manufacture balance: state the evidence you hold, withhold only the conclusion.

Directive wording is correct when the author has already decided, when safety or
legality is at stake, when an external contract dictates the outcome, when an
outcome is genuinely inadmissible and named as such, or when the decision is small
enough that one balanced sentence carries the whole frame.
```

</details>

## The scanner

The scanner and eval harness are repository scripts, not part of the installed
skill. To use them, clone the repository and run them against your prompt files:

```bash
git clone https://github.com/skyRolly/neutral-prompt
cd neutral-prompt
python3 scripts/scan_prompt.py path/to/prompt.md
```

Python 3.9 or newer, no third-party packages. See [evals/README.md](evals/README.md)
for the measured detection coverage.

## How activation works

1. **Installed, not invoked.** In Claude Code, Qwen Code, and Codex, nothing
   happens until you invoke the skill explicitly. Claude Code and Qwen Code honor
   `disable-model-invocation: true` in `SKILL.md`; Codex honors
   `policy.allow_implicit_invocation: false` in `agents/openai.yaml`. Other
   harnesses may load every skill's description at startup and activate the skill
   themselves.
2. **You invoke it explicitly.** Type `/neutral-prompt` in Claude Code or Qwen
   Code, or `$neutral-prompt` in Codex. The rules stay on for that session.
   "stop neutral mode" or "normal mode" turns them off.
3. **You touch `~/.claude/.neutral-prompt-always`** (Claude Code). A
   `SessionStart` hook loads the full ruleset from message one, every session.
4. **You add the always-on snippet above** (other harnesses). Keeps the core rules
   in your agent's persistent context.

In Claude Code, Qwen Code, and Codex there is no middle ground: if you did not
turn it on, it is off.

## Troubleshooting

**`/neutral-prompt` not in autocomplete.** Restart the agent. The plugin index is
read at startup.

**Always-on flag has no effect.** Update the plugin
(`claude plugin marketplace update neutral-prompt`) and restart. Hooks are read
at startup, and the flag needs the plugin version that ships `hooks/hooks.json`.

**`claude plugin marketplace add` fails.** Use the `owner/repo` form. A local path
must point at the repo root, not `.claude-plugin/`.

**Installed, but prompts still read as directional.** Open a new session. If it
still drifts, run `python3 scripts/scan_prompt.py` over the prompt to see which
rule it trips, then tighten the wording in `skills/neutral-prompt/SKILL.md`.

**The scanner flags a constraint that is correct as written.** That is expected —
it matches phrasings, not intent. Suppress it with `neutral-prompt: allow NP003`
on the line or the line above, and say in the surrounding text why the phrase is a
settled constraint.

**Skill missing after `npx skills add`.** Start a new agent chat. Skills are
indexed at session start. Confirm the folder landed where your agent scans
(`~/.cursor/skills/` for Cursor, `.agents/skills/` for OpenCode) and that the
frontmatter `name` matches the folder name.
