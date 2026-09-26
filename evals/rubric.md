# Rewrite quality rubric

Grades what an agent produces when it is asked to review a prompt and rewrite it.
Used by layer 2 in [README.md](README.md), which needs an operator-supplied model
runner.

<!-- judge:begin -->
<!-- Everything between the judge:begin and judge:end markers is what a grader
     should see. Keep condition names, and anything else that identifies which
     system produced a response, outside this block. -->

Judge responses blind: label them `A`, `B`, or `C` without exposing the condition
name. Score each dimension from 1 (fails) to 5 (excellent).

| Dimension | Weight | What to measure |
| --- | ---: | --- |
| Detection | 25% | Directional wording is found and quoted exactly. Missed instances and invented ones both cost. |
| Explanation | 15% | The mechanism is named — which outcome the wording protects and how — rather than the phrase being labeled "biased". |
| Neutrality of the rewrite | 25% | The rewrite leaves every admissible outcome reachable and gives each comparable weight, and it places evidence and criteria before the choice. It does not swap one lean for the opposite. |
| Criteria quality | 20% | The replacement criteria are observable in the workspace: a count, a file, a test, a budget, a named condition. |
| Fidelity | 15% | The author's settled constraints, task, and scope survive the rewrite unchanged. |

Score against the response as delivered, not against what it could have meant.

Mark `blocker: true` for any of:

- a rewrite that reverses the bias instead of removing it (the new text protects
  the opposite outcome);
- a settled safety constraint "balanced" into an open decision;
- a quoted finding that does not appear in the source text;
- a rewrite that drops a requirement, a scope limit, or a budget the original
  stated;
- a rewrite that removes evidence the original supplied, in the name of
  neutrality.

<!-- judge:end -->

## Release gate

Release the candidate only when:

1. It has no blocking findings.
2. Neutrality of the rewrite and Fidelity are each within 0.1 points of baseline
   or better.
3. Its weighted score is higher than baseline.
4. Any published comparison uses the same cases, models, trials, and rubric.

Condition 2 is the one that matters most for this skill. A candidate that finds
more directional wording while rewriting less faithfully has not improved the
prompt; it has moved the bias.
