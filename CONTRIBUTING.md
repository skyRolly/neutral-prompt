# Contributing

Thanks for improving **neutral-prompts**. Contributions from humans and coding
agents are welcome. Keep changes understandable, reviewable, safe to run, and
compatible with existing users.

## Authorship and provenance

Every pull request must select exactly one category:

- **Human-authored** — a human made the substantive implementation and text.
  Autocomplete, formatting, search, and minor suggestions do not make a
  contribution hybrid.
- **Autonomous agent-authored** — an agent made most substantive decisions and
  changes, with a human primarily providing the task and reviewing the result.
- **Hybrid** — a human and one or more agents both made substantive decisions or
  changes.

For autonomous-agent or hybrid contributions, disclose the agent or tool and
model/version when known, what it did, what the human reviewed, and any material
limitations or failed checks. Do not call generated work human-authored or
independently verified when it was only reviewed by the same agent that produced
it.

The submitting human remains accountable for the full diff. Before submission,
read the changed files, remove unrelated generated changes, and verify the claims
in the PR description.

## Scope and reviewability

Keep each PR focused. Avoid drive-by formatting, unrelated dependency changes,
generated filler, and broad rewrites that make behavior changes difficult to
inspect.

The PR description must explain:

1. what changed and why;
2. observable behavior before and after;
3. safety, compatibility, and side-effect considerations;
4. the exact verification performed.

Discuss large behavior changes, new integrations, new hooks, and potentially
breaking changes in an issue first.

## Adding or changing a scanner rule

A rule exists in three places, and the checks fail until all three agree:

1. **The catalog** — an entry in
   `skills/neutral-prompts/references/patterns.md` with an id, a detection cue,
   the mechanism, and a neutral replacement.
2. **The detector** — a `Rule` in `scripts/scan_prompt.py` with the same id, a
   severity, a `why` sentence, and a `suggestion`.
3. **The labels** — at least one case in `evals/cases.jsonl` whose `expect` lists
   the id, plus a neutral case that the rule must not fire on.

Then run:

```bash
python3 scripts/run_evals.py scan
python3 -m unittest discover -s tests
```

Severity guidance: **high** for a pattern that protects one action outright;
**medium** for one that biases through cost or vagueness; **advisory** for a
whole-document check that fires on absence and therefore over-reports.

When a rule fires on text that is correct as written, that is a false positive
worth recording rather than hiding. Add the text as a `kind: "neutral"` case
whose `expect` lists the rule, and explain the limitation in the case's `note`.
`run_evals.py scan` reports these separately as known scanner limitations.

## Writing rules and examples

Skill changes must stay focused on prompt framing and decision quality. Two
requirements specific to this repository:

- **The skill must not become directional itself.** A rule that pushes agents
  toward continuing, stopping, changing, preserving, accepting, or rejecting
  contradicts the skill's purpose. Rules constrain *how* a decision is framed,
  never *which* outcome is chosen.
- **Label every quoted example of the biased form.** Documentation here quotes
  directional wording to diagnose it. An unlabeled quote reads as a
  recommendation.

Keep terminology consistent with `SKILL.md`: *open decision*, *settled
constraint*, *admissible outcome*, *decision criteria*, *protected action*,
*decision record*, and the seven outcomes (proceed, stop, modify, preserve,
accept, reject, defer).

## Safety and side effects

Contributions must not weaken platform safeguards, override higher-priority
instructions, conceal risky behavior, or encourage inaccurate claims.

Do not add instructions, examples, fixtures, or tests that tell an agent to:

- read or transmit credentials, tokens, environment variables, private files, or
  repository data;
- modify shell profiles, global Git configuration, editor settings, or unrelated
  agent configuration;
- bypass confirmation for destructive, privileged, production, or externally
  visible actions;
- silently install software, fetch and execute remote code, or create
  persistence.

Neutral framing does not extend to safety constraints. A prompt that requires
confirmation before a destructive action is stating a settled constraint, and
"balancing" it would be a defect, not a fix.

Installation, activation, validation, and tests must be narrowly scoped and
predictable. By default, repository code must not modify files outside the
repository or a documented temporary directory, alter user configuration or
credentials, publish or send data, require elevated privileges, perform
irreversible actions, or leave background processes behind.

## Hooks and scripts

Hooks run in user environments: keep them fast, bounded, fail-safe, opt-in, and
free of network access. An optional failure must not block agent startup — the
`SessionStart` hook exits 0 on every error path, and
`tests/test_repo_integrity.py` covers that.

Scripts must validate inputs and paths, avoid shell commands built from untrusted
text, use temporary fixtures, and use least privilege. The scanner and the eval
harness are standard-library Python 3.9+ with no network access and no model
calls; keep them that way. A new third-party dependency needs a clear
justification in the PR.

## Compatibility and breaking changes

Preserve existing installation methods, invocation names, file locations, opt-in
behavior, and supported integrations unless a breaking change is explicitly
accepted. Potentially breaking changes include moving the canonical skill,
changing invocation or hook semantics, renaming or removing a scanner rule id,
changing manifests or installation commands, and removing a supported platform.

A breaking change requires an issue, a migration path, updated documentation, and
a compatibility or deprecation plan. Prefer additive, staged changes. Retire a
scanner rule id rather than reusing it for a different pattern.

`skills/neutral-prompts/SKILL.md` is canonical. When it changes, synchronize the
Cursor copy:

```sh
cp skills/neutral-prompts/SKILL.md .cursor/skills/neutral-prompts/SKILL.md
cmp skills/neutral-prompts/SKILL.md .cursor/skills/neutral-prompts/SKILL.md
```

Review platform-specific manifests and documentation whenever shared names,
descriptions, paths, or behavior change. Bump the version in every versioned
manifest together; `tests/test_repo_integrity.py` fails when they drift.

## Verification

Run the relevant checks and include the commands and results in the PR:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/run_evals.py validate
python3 scripts/run_evals.py scan
```

For a behavior change to the skill rules, add or update representative cases and
say what the scan reported before and after. For a hook or manifest change,
verify loading in an isolated configuration directory. If a check was not run,
say so and explain why; never invent results or treat inspection as execution.

## Documentation and checklist

Keep examples safe to copy: harmless fixtures, explicit placeholders, read-only
previews. Never include real secrets, personal paths, or production identifiers.
Distinguish required behavior from suggestions, and avoid unsupported claims
about platform support or measured effectiveness.

A PR is ready when:

- one authorship category is selected and agent involvement is disclosed
  accurately;
- the full diff has been reviewed by a human contributor;
- the change is focused and free of unrelated generated edits;
- side effects, compatibility, and verification are documented.

Maintainers may close PRs that conceal provenance, introduce unsafe behavior,
lack verification, or make unplanned breaking changes.
