# Evaluations

Two layers, measuring two different things.

**Layer 1 — the detector.** `scripts/scan_prompt.py` is measured against the
labeled cases in `cases.jsonl`. This layer runs offline, calls no model, costs
nothing, and gates every change to a scanner rule.

**Layer 2 — the rewrites.** `rubric.md` grades what an agent produces when it
reviews and rewrites a prompt. This layer needs a model runner, which this
repository does not ship: supply your own and record the conditions with any
published numbers.

## Layer 1: detector coverage

```bash
python3 scripts/run_evals.py validate   # schema-check the case file
python3 scripts/run_evals.py scan       # run the scanner and compare to the labels
python3 scripts/run_evals.py scan --json
```

`scan` exits 0 only when every case produces exactly the rule ids its label
names — extra findings fail as loudly as missing ones, so a rule that widens into
a false positive is caught by the same run that checks its recall.

### Case format

One JSON object per line:

```json
{"id":"lifecycle-protected-stop","category":"lifecycle","kind":"directional","text":"...","expect":["NP001","NP012"],"note":"why this label is what it is"}
```

| Field | Meaning |
| --- | --- |
| `id` | Unique, kebab-case, prefixed with its category (`accept-` for `accept-reject`). |
| `category` | `lifecycle`, `review`, `investigation`, `accept-reject`, or `general`. `validate` rejects any other value. |
| `kind` | `directional` — the text is biased. `neutral` — the text is correct as written. |
| `text` | The prompt fragment handed to the scanner, verbatim. |
| `expect` | The exact set of rule ids the scanner must report. |
| `note` | Why the label is what it is. Required; a label without a reason cannot be reviewed. |

A `neutral` case with a non-empty `expect` is a **known scanner limitation**: text
that is correct as written but still matches a pattern. These are recorded rather
than hidden, and `scan` lists them separately.

### Current state

Measured with the shipped case file on Python 3.11:

| | |
|---|---|
| Cases | 27 (19 directional, 8 neutral) |
| Categories | lifecycle 7, review 8, investigation 5, accept-reject 4, general 3 |
| Rules with at least one labeled case | 12 of 12 |
| Cases matching their label | 27 of 27 |
| Known scanner limitations | 2 |

The two known limitations are both cases where the phrase is a settled constraint
or is balanced by a neighbouring sentence:

- `lifecycle-paired-negations` — the negation is paired in the following
  sentence, which the line-by-line scanner cannot weigh. Flags NP001.
- `review-scope-constraint` — a directory boundary is a settled constraint, not a
  lean. Flags NP003.

Both are the expected shape of the tool's limits: it matches phrasings, not
intent. Suppress a confirmed false positive with `neutral-prompt: allow NP003`
on the line or the line above.

### What this number is not

Detector coverage measures the scanner against text somebody hand-labeled. It
does not measure how often directional wording appears in real prompts, and it
does not measure whether an agent writes better prompts after loading the skill.
Three of the failures the skill targets — missing outcomes, asymmetric intensity,
and ordering — have no reliable textual cue and are absent from this layer
entirely. Layer 2 is where those are graded.

## Layer 2: rewrite quality

`rubric.md` defines the dimensions and the release gate for grading an agent's
prompt review and rewrite. Running it needs three things this repository does not
provide: a model runner, a budget, and a set of task prompts.

Keep the comparison honest:

- **Isolate the call from your own agent configuration.** User-level plugins,
  hooks, memory, and output styles otherwise leak into every condition. The
  sharpest case is this repository's own always-on flag
  (`~/.claude/.neutral-prompt-always`), which would inject the full ruleset into
  the *baseline* condition and make the comparison measure the skill against
  itself.
- **Pin the model explicitly.** Isolation drops saved model and effort settings,
  so an unpinned run silently uses whatever the operator or the CLI release
  defaults to. The pinned model is part of the result.
- **Blind the grader.** Relabel conditions before grading and permute the label
  order, so position carries no signal. Send the grader only the text between the
  `<!-- judge:begin -->` and `<!-- judge:end -->` markers in `rubric.md`; the
  release gate below them names the conditions.
- **Hold the cases fixed.** Do not compare conditions produced with different
  cases, models, trial counts, or rubrics.

The rubric grades one review and rewrite, so it does not test the Persistence
section of `SKILL.md`: that the rules still apply after the topic changes, and
that "stop neutral mode" or "normal mode" turns them off with a one-line
confirmation. Testing that takes one resumed conversation in which the skill is
supplied with the first turn, followed by at least one turn on an unrelated
topic, then a review-and-rewrite task, then the off-switch. Grade that rewrite
with the rubric against the same task given as the first turn of a fresh
candidate session, so the task is held fixed, and send the grader only the two
rewrites, not the transcripts. Then check that the reply to the off-switch is
one line. No scenario of that shape ships here; capturing one needs the model
runner this repository does not ship.

Record the runner, the CLI version, the model, the case count, the trial count,
the rubric revision, and the reported token usage and cost alongside any numbers
you publish. A candidate call carries the skill text that a baseline call does
not, so the input-token difference is part of the result. Keep raw runs under
`evals/results/`, which is git-ignored.
