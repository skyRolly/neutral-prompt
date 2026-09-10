## Summary

<!-- What changed, why it is needed, and the observable behavior before and after. -->

## Authorship and provenance — select exactly one

- [ ] **Human-authored** — substantive implementation and text were produced by a human.
- [ ] **Autonomous agent-authored** — an agent planned and produced most of the substantive change.
- [ ] **Hybrid** — a human and one or more agents both made substantive contributions.

**Agent/tool and model/version:** <!-- Write "None" for human-authored PRs. -->

**Agent contribution:** <!-- Planning, code, tests, docs, review, or other work. -->

**Human verification:** <!-- What the submitting human personally reviewed and ran. -->

**Known limitations or uncertain results:** <!-- Write "None known" only after review. -->

## Neutrality

- [ ] No rule, example, or default in this change pushes an agent toward continuing, stopping, changing, preserving, accepting, or rejecting.
- [ ] Every quoted example of directional wording is labeled as an example, not as a recommendation.
- [ ] Settled constraints (safety, scope, budgets, output contracts) stay directive and were not "balanced" into open decisions.
- [ ] Terminology matches `SKILL.md`: open decision, settled constraint, admissible outcome, decision criteria, protected action, decision record.

## Scanner rules — complete this section when a rule is added or changed

- [ ] Catalog entry in `skills/neutral-prompt/references/patterns.md`.
- [ ] `Rule` in `scripts/scan_prompt.py` with the same id, a severity, a `why`, and a `suggestion`.
- [ ] At least one `directional` case in `evals/cases.jsonl` that the rule must catch.
- [ ] At least one `neutral` case the rule must not fire on, or a recorded known limitation with a `note`.
- [ ] No existing rule id was reused for a different pattern.

## Safety and side effects

- [ ] The change does not access or expose secrets, private files, or unrelated user/repository data.
- [ ] Scripts, hooks, and workflows are bounded and create no surprising or irreversible side effects.
- [ ] No destructive, privileged, production, externally visible, or persistent action occurs without explicit user intent.
- [ ] Network access, third-party code, and permissions are minimized and documented.
- [ ] Prompt text, examples, and fixtures contain no hidden instructions that weaken safety or expand agent authority.

**Side effects, permissions, and network access:**

<!-- State "None" when applicable; otherwise describe exact scope and rollback. -->

## Compatibility

- [ ] This is not a breaking change.
- [ ] This is a breaking change; it was discussed, and migration/deprecation notes are below.
- [ ] The canonical skill and the `.cursor` mirror are synchronized.
- [ ] Versioned manifests were bumped together, and installation docs were reviewed.

**Migration or rollback notes:**

## Verification

<!-- List only commands actually run and their results. Remove unrun examples. -->

- `python3 -m unittest discover -s tests -v` — <!-- result -->
- `python3 scripts/run_evals.py scan` — <!-- result -->

## Final accountability

- [ ] I reviewed the complete diff, removed unrelated generated changes, and take responsibility for the submitted content.
- [ ] All failed, skipped, or unrun checks are disclosed above.
