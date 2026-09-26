<p align="center">
  <strong>Prompts that frame a decision instead of pre-answering it.</strong>
</p>
<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/skyRolly/neutral-prompt?style=flat" alt="License"></a>
</p>

## Install

Copy/paste into your CLI prompt:

```text
Install the neutral-prompt skill/plugin from https://github.com/skyRolly/neutral-prompt, refer to the repo's AGENTS.md for instructions.
```

Or 🔗 [check the installation instructions](INSTALL.md).

## What it does

A skill for your coding assistant that stops prompts from carrying the answer.
Every prompt that hands a decision to an agent also hands it a prior — "do not
stop them" is read as *continue*, "avoid unnecessary changes" as *prefer the
existing code*. This skill finds that wording, explains why it biases, and
rewrites it as a decision the evidence settles.

It does not push agents toward continuing, stopping, changing, preserving,
accepting, or rejecting. It pushes them toward deciding well.

## What changes

<table>
<tr>
<td width="50%">

## Before

> You have several workflow agents still running. Do NOT immediately stop them.
> Check what they are doing first.

The negation is the only instruction with force. "Check what they are doing" has
no criterion attached, so the check produces a description rather than a
decision — and stopping now requires overriding the prompt.

</td>

<td width="50%">

## After

> Four workflow agents are still running. Decide the disposition of each one.
>
> Do not assume they should be stopped. Do not assume they should continue.
>
> 1. **Gather** — read each agent's recent outputs and remaining scope.
> 2. **Evaluate** — compare that scope against findings already in the report.
> 3. **Choose** — continue · consume results and stop · stop as redundant · defer.
> 4. **Record** — evidence, alternatives, action, reasoning.
>
> Continue when the remaining steps target a file no completed agent has
> reported on. Consume and stop when its findings have landed and the rest
> repeats covered ground. Stop as redundant when the report already covers its
> whole scope. Defer when one more output would settle which applies.

</td>
</tr>
</table>

## The rules

10 rules. Full text in [SKILL.md](./skills/neutral-prompt/SKILL.md).

1. Separate settled constraints from open decisions.
2. Name the decision, not the answer.
3. List every admissible outcome.
4. Balance the negations.
5. Replace protected actions with decision criteria.
6. Order the prompt: evidence, alternatives, choice, record.
7. Keep the intensity symmetric.
8. Make the thresholds observable.
9. Require the decision record, not the decision.
10. Do not manufacture balance.

They govern **open decisions** — the choices a prompt delegates. They do not
govern settled constraints: safety rules, output contracts, budgets, standards.
Directive wording is the correct form for a constraint.

## The scanner

A prompt linter ships with the repo. It flags the twelve patterns catalogued in
[`references/patterns.md`](./skills/neutral-prompt/references/patterns.md). Here
it is on the Before prompt above, saved as plain text in `my-prompt.md`:

```console
$ python3 scripts/scan_prompt.py my-prompt.md
my-prompt.md:1:1  NP012  advisory  '(whole document)'
    why: The text delegates a lifecycle or review decision but states no criteria, so the agent falls back on tone, on its own defaults, or on whichever outcome was named first.
    try: Name the admissible outcomes and the observable condition that selects each one.
my-prompt.md:1:49  NP001  high      'Do NOT immediately stop'
    why: A negated stop verb protects continuation: the complement becomes the default and needs no justification.
    try: Name the decision instead: 'Evaluate each one. Continuing and stopping are both admissible outcomes.'
2 finding(s): 1 high, 0 medium, 1 advisory
```

It finds phrasings, not intent. A hit on a settled constraint is correct as
written — confirm what each phrase governs, then suppress the ones that are fine
with `neutral-prompt: allow NP001` on the line or the line above.

Measure it against the labeled cases in [`evals/`](./evals/README.md):

```bash
python3 scripts/run_evals.py scan
```

## Tune it

Fork, edit `skills/neutral-prompt/SKILL.md`, then swap your copy in:

```bash
claude plugin uninstall neutral-prompt            # drop the upstream copy first:
claude plugin marketplace remove neutral-prompt   # fork and upstream share both names
claude plugin marketplace add <your-username>/neutral-prompt
claude plugin install neutral-prompt@neutral-prompt
```

Restart Claude Code, then re-invoke `/neutral-prompt`.

Adding a rule to the scanner means adding an entry to `references/patterns.md`, a
`Rule` in `scripts/scan_prompt.py`, and a labeled case in `evals/cases.jsonl`. The
unit tests fail until all three agree, and `python3 scripts/run_evals.py scan`
fails when any case's findings differ from its label. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE).
