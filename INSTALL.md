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
claude plugin update neutral-prompt@neutral-prompt
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
3. List every admissible outcome, drawn from: proceed, stop, modify, preserve, accept, reject, defer.
4. Balance the negations — ruling out one default installs its opposite.
5. Replace protected actions ("do not stop", "avoid changing", "always fix") with the criterion they were hiding.
6. Order the prompt: gather evidence, evaluate alternatives, choose an action, record the reasoning.
7. Keep the intensity symmetric across outcomes; "must continue" against "may stop" is a ranking.
8. Make thresholds observable — replace "enough", "sufficient", "significant", "reasonable", "as needed", "premature".
9. Require the decision record, not a particular decision.
10. Do not manufacture balance: state the evidence you hold, withhold only the conclusion.

Directive wording is correct when the author has already decided, when safety,
legality, or destructiveness is at stake, when an external contract dictates the
outcome, when an outcome is genuinely inadmissible and named as such, or when the
text quotes a biased form in order to diagnose it. A decision with two obvious
outcomes and one obvious criterion gets one balanced sentence instead of the full
frame.
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

Start a new session, type `/neutral-prompt`. It stays on for that session; "stop
neutral mode" or "normal mode" turns it off.

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
`~/.copilot/skills/` and `~/.agents/skills/` globally (Copilot in VS Code also
reads `~/.claude/skills/`).

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

In VS Code, type `/` in the chat input and confirm `neutral-prompt` appears. In
Copilot CLI, run `/skills list`. Or:

```bash
npx skills list
npx skills ls -g    # if installed globally
```

### Update

```bash
npx skills update neutral-prompt
npx skills update neutral-prompt -g    # if installed globally
```

Or re-copy the folder after `git pull`.

### Uninstall

```bash
npx skills remove neutral-prompt
npx skills remove neutral-prompt -g    # if installed globally
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
3. List every admissible outcome, drawn from: proceed, stop, modify, preserve, accept, reject, defer.
4. Balance the negations — ruling out one default installs its opposite.
5. Replace protected actions ("do not stop", "avoid changing", "always fix") with the criterion they were hiding.
6. Order the prompt: gather evidence, evaluate alternatives, choose an action, record the reasoning.
7. Keep the intensity symmetric across outcomes; "must continue" against "may stop" is a ranking.
8. Make thresholds observable — replace "enough", "sufficient", "significant", "reasonable", "as needed", "premature".
9. Require the decision record, not a particular decision.
10. Do not manufacture balance: state the evidence you hold, withhold only the conclusion.

Directive wording is correct when the author has already decided, when safety,
legality, or destructiveness is at stake, when an external contract dictates the
outcome, when an outcome is genuinely inadmissible and named as such, or when the
text quotes a biased form in order to diagnose it. A decision with two obvious
outcomes and one obvious criterion gets one balanced sentence instead of the full
frame.
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
5. Run `/reload` or start a new session; the current session does not pick up a
   new plugin until then.

Use the slash command `/skill:neutral-prompt` to invoke the skill explicitly.

### Update

`/plugins` in a Kimi Code session, open the **Installed** tab, cursor to **Neutral
Prompts**, and press `Enter`; it updates when a newer version is available (`R`
only reloads the installed manifests). Then run `/reload` or start a new session.

### Uninstall

`/plugins` in a Kimi Code session, cursor to **Neutral Prompts**, press `D`, then
run `/reload` or start a new session.

</details>

<details>
<summary><strong>OpenCode</strong></summary>

OpenCode reads Agent Skills natively: the same `SKILL.md`, no conversion. It scans
`.opencode/skills/`, `.claude/skills/`, and `.agents/skills/` in the project, and
`~/.config/opencode/skills/`, `~/.claude/skills/`, and `~/.agents/skills/`
globally. The repository also ships `.opencode/command/neutral-prompt.md`, which
adds a `/neutral-prompt` command to a project that has it. The command tells the
agent to use the skill, so install the skill as well.

### Install

```bash
npx skills add skyRolly/neutral-prompt -a opencode -y       # this project: .agents/skills/
npx skills add skyRolly/neutral-prompt -a opencode -g -y    # all projects: ~/.config/opencode/skills/
```

The CLI installs the skill only. To add the `/neutral-prompt` command file as
well, or to install without the CLI, copy both pieces by hand:

```bash
git clone https://github.com/skyRolly/neutral-prompt
mkdir -p ~/.config/opencode/skills ~/.config/opencode/command
cp -R neutral-prompt/skills/neutral-prompt ~/.config/opencode/skills/
cp neutral-prompt/.opencode/command/neutral-prompt.md ~/.config/opencode/command/
```

### Verify

Start OpenCode and ask the agent to load the `neutral-prompt` skill. OpenCode hands
installed skills to the agent through its `skill` tool, so a successful load is
the check. If you also copied the command file, type `/` and confirm
`neutral-prompt` is listed. The `/` list shows command files and omits skills, so
this second check does not apply to the CLI route.

### Update

```bash
npx skills update neutral-prompt
npx skills update neutral-prompt -g    # if installed globally
```

Or re-copy after `git pull`.

### Uninstall

```bash
npx skills remove neutral-prompt        # CLI route
npx skills remove neutral-prompt -g     # CLI route, if installed globally
```

For the manual route, delete `~/.config/opencode/skills/neutral-prompt` and
`~/.config/opencode/command/neutral-prompt.md`.

### Always-on (optional)

Add to `~/.config/opencode/AGENTS.md`:

```markdown
## Prompt framing

Apply these rules to every prompt you write, review, or rewrite. They govern open
decisions — the choices a prompt delegates — not settled constraints such as
safety rules, output contracts, budgets, or coding standards.

1. Separate settled constraints from open decisions; write constraints as imperatives.
2. Name the decision, not the answer.
3. List every admissible outcome, drawn from: proceed, stop, modify, preserve, accept, reject, defer.
4. Balance the negations — ruling out one default installs its opposite.
5. Replace protected actions ("do not stop", "avoid changing", "always fix") with the criterion they were hiding.
6. Order the prompt: gather evidence, evaluate alternatives, choose an action, record the reasoning.
7. Keep the intensity symmetric across outcomes; "must continue" against "may stop" is a ranking.
8. Make thresholds observable — replace "enough", "sufficient", "significant", "reasonable", "as needed", "premature".
9. Require the decision record, not a particular decision.
10. Do not manufacture balance: state the evidence you hold, withhold only the conclusion.

Directive wording is correct when the author has already decided, when safety,
legality, or destructiveness is at stake, when an external contract dictates the
outcome, when an outcome is genuinely inadmissible and named as such, or when the
text quotes a biased form in order to diagnose it. A decision with two obvious
outcomes and one obvious criterion gets one balanced sentence instead of the full
frame.
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

Type `/neutral-prompt:neutral-prompt` to invoke the skill explicitly; Qwen Code
registers an extension's skills as `<extension>:<skill>`. Installing the
extension does not change behavior until the skill is invoked.

### Verify

```bash
qwen extensions list
```

Then start a new Qwen Code session and run:

```text
/skills
```

Confirm that `neutral-prompt:neutral-prompt` appears in the list.

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

Open the command palette, run `agent: create skill from url`, and paste:

```
https://github.com/skyRolly/neutral-prompt/blob/main/skills/neutral-prompt/SKILL.md
```

Save it in **User** scope for every project, or **Project** scope for one. Then
type `/neutral-prompt` in the Agent Panel.

URL import brings `SKILL.md` alone. The reference files it links to
(`references/patterns.md`, `references/examples.md`, `references/decision-record.md`)
come only with the folder copy below.

Prefer the filesystem? Clone the repo and copy the skill folder into
`~/.agents/skills/`, the global directory Zed scans:

```bash
git clone https://github.com/skyRolly/neutral-prompt
mkdir -p ~/.agents/skills
cp -R neutral-prompt/skills/neutral-prompt ~/.agents/skills/
```

### Verify

Open the Skills manager in the Agent Panel and confirm `neutral-prompt` is
listed. Or type `/` and confirm it appears.

### Update

Delete `neutral-prompt` in the Skills manager and import it again from the same
URL, or re-copy the folder after `git pull`.

### Uninstall

Remove `neutral-prompt` from the Skills manager, or delete
`~/.agents/skills/neutral-prompt`.

### Always-on (optional)

Add to your personal `~/.config/zed/AGENTS.md`:

```markdown
## Prompt framing

Apply these rules to every prompt you write, review, or rewrite. They govern open
decisions — the choices a prompt delegates — not settled constraints such as
safety rules, output contracts, budgets, or coding standards.

1. Separate settled constraints from open decisions; write constraints as imperatives.
2. Name the decision, not the answer.
3. List every admissible outcome, drawn from: proceed, stop, modify, preserve, accept, reject, defer.
4. Balance the negations — ruling out one default installs its opposite.
5. Replace protected actions ("do not stop", "avoid changing", "always fix") with the criterion they were hiding.
6. Order the prompt: gather evidence, evaluate alternatives, choose an action, record the reasoning.
7. Keep the intensity symmetric across outcomes; "must continue" against "may stop" is a ranking.
8. Make thresholds observable — replace "enough", "sufficient", "significant", "reasonable", "as needed", "premature".
9. Require the decision record, not a particular decision.
10. Do not manufacture balance: state the evidence you hold, withhold only the conclusion.

Directive wording is correct when the author has already decided, when safety,
legality, or destructiveness is at stake, when an external contract dictates the
outcome, when an outcome is genuinely inadmissible and named as such, or when the
text quotes a biased form in order to diagnose it. A decision with two obvious
outcomes and one obvious criterion gets one balanced sentence instead of the full
frame.
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
npx skills update neutral-prompt -g    # if installed globally
```

### Uninstall

```bash
npx skills remove neutral-prompt
npx skills remove neutral-prompt -g    # if installed globally
```

### Always-on (optional)

Paste this into your agent's persistent rules file. Cursor: **Customize → Rules**
(User Rules), or a project rule file under `.cursor/rules/` with the `.mdc`
extension and `alwaysApply: true` in its frontmatter.

```markdown
## Prompt framing

Apply these rules to every prompt you write, review, or rewrite. They govern open
decisions — the choices a prompt delegates — not settled constraints such as
safety rules, output contracts, budgets, or coding standards.

1. Separate settled constraints from open decisions; write constraints as imperatives.
2. Name the decision, not the answer.
3. List every admissible outcome, drawn from: proceed, stop, modify, preserve, accept, reject, defer.
4. Balance the negations — ruling out one default installs its opposite.
5. Replace protected actions ("do not stop", "avoid changing", "always fix") with the criterion they were hiding.
6. Order the prompt: gather evidence, evaluate alternatives, choose an action, record the reasoning.
7. Keep the intensity symmetric across outcomes; "must continue" against "may stop" is a ranking.
8. Make thresholds observable — replace "enough", "sufficient", "significant", "reasonable", "as needed", "premature".
9. Require the decision record, not a particular decision.
10. Do not manufacture balance: state the evidence you hold, withhold only the conclusion.

Directive wording is correct when the author has already decided, when safety,
legality, or destructiveness is at stake, when an external contract dictates the
outcome, when an outcome is genuinely inadmissible and named as such, or when the
text quotes a biased form in order to diagnose it. A decision with two obvious
outcomes and one obvious criterion gets one balanced sentence instead of the full
frame.
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

1. **Installed, not invoked.** In Claude Code, Codex, Qwen Code, Kimi Code CLI,
   Zed, Cursor, and Copilot (VS Code and CLI), nothing happens until you invoke the
   skill explicitly. Codex honors `policy.allow_implicit_invocation: false` in
   `agents/openai.yaml`; the others honor `disable-model-invocation: true` in
   `SKILL.md`. OpenCode ignores that field and Gemini CLI does not document it, so
   those harnesses may load the skill's description at startup and activate the
   skill themselves.
2. **You invoke it explicitly.** Type `/neutral-prompt` in Claude Code, Zed,
   Cursor, or Copilot; `/neutral-prompt:neutral-prompt` in Qwen Code;
   `/skill:neutral-prompt` in Kimi Code CLI; or `$neutral-prompt` in Codex. The
   rules stay on for that session. "stop neutral mode" or "normal mode" turns them
   off.
3. **You touch `~/.claude/.neutral-prompt-always`** (Claude Code). A
   `SessionStart` hook loads the full ruleset from message one, every session.
4. **You add the always-on snippet above** (other harnesses). Keeps the core rules
   in your agent's persistent context.

In the harnesses that item 1 names as honoring those fields there is no middle
ground: if you did not turn it on, it is off.

## Troubleshooting

**`/neutral-prompt` not in autocomplete.** Restart the agent. The plugin index is
read at startup.

**Always-on flag has no effect.** Update the plugin
(`claude plugin update neutral-prompt@neutral-prompt`) and restart. Hooks are read
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
