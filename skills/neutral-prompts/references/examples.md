# Worked examples

Whole-prompt rewrites, one per domain. Each shows the original, what a reader
does with it, the finding table, and the replacement.

The "before" text in every example is a demonstration of the biased form. It is
quoted to be diagnosed, not copied.

---

## 1. Sub-agent lifecycle

### Before

> You have several workflow agents still running. Do NOT immediately stop them.
> Check what they are doing first.

### What an agent does with it

The negation is the only instruction with force. "Check what they are doing" has
no criterion attached, so the check produces a description rather than a
decision, and the agent returns to the one clear directive: leave them running.
Stopping now requires overriding the prompt, which needs evidence the prompt
never asks for.

### Findings

| Quoted text | Rule | Why it biases |
| --- | --- | --- |
| "Do NOT immediately stop them." | NP001 | Negation protects continuation; the decision becomes an action constraint. |
| "immediately" | NP001 | Reads as "not yet", which is still a lean, and leaves the criterion unwritten. |
| "Check what they are doing first." | NP012 | Names an inspection with no criteria and no outcome list, so the inspection cannot change anything. |
| (absent) | Outcomes | Consume-and-stop and defer are admissible and unnamed. |

### After

> Four workflow agents are still running. Decide the disposition of each one
> independently.
>
> Do not assume they should be stopped. Do not assume they should continue. Both
> are outcomes of the evaluation below, not inputs to it.
>
> 1. **Gather.** For each agent, read its most recent outputs and its current
>    status. Note which files and questions its remaining steps target.
> 2. **Evaluate.** Compare that remaining scope against findings already in the
>    report. Note where they overlap and where they do not.
> 3. **Choose** one outcome per agent:
>    - **Continue** — its remaining steps target a question no completed agent
>      has answered.
>    - **Consume results and stop** — its findings have landed and its remaining
>      steps repeat covered ground.
>    - **Stop as redundant** — its scope is fully covered by findings already in
>      the report.
>    - **Defer** — one more output would settle which of the above applies.
> 4. **Record.** For each agent: the outputs you read, the outcomes you compared,
>    the action taken, and the reasoning.
>
> Constraints: read an agent's output before discarding it. Budget for remaining
> execution: 15 minutes total.

### What changed

The decision moved from the wording to the evidence. Both directions are now
reachable, each has an observable criterion, and the record makes either choice
defensible. The 15-minute budget stayed an imperative — it is a settled
constraint, not a decision.

---

## 2. Code review finding

### Before

> Review the diff. Do not make unnecessary changes, and make sure you fix
> anything the reviewer flagged.

### What an agent does with it

The two halves point in opposite directions, and the agent resolves the conflict
by authorship: reviewer-flagged items get changed, everything else gets left
alone. A real defect the reviewer missed goes unfixed; an incorrect review
comment gets "fixed" anyway.

### Findings

| Quoted text | Rule | Why it biases |
| --- | --- | --- |
| "Do not make unnecessary changes" | NP003 | "Unnecessary" is decided after the fact, so it applies in advance to everything. |
| "make sure you fix anything the reviewer flagged" | NP004, NP005 | Converts a scoping decision into an obligation and replaces evaluation with authorship. |
| (absent) | Outcomes | Reject-with-reasoning and defer are admissible and unnamed. |

### After

> Review the diff and decide the disposition of each finding — your own and the
> reviewer's.
>
> Do not modify code without evidence. Do not preserve code merely because it
> already exists. Authorship carries no weight: a finding from the reviewer, a
> bot, or your own reading is evaluated the same way.
>
> **Evidence to gather per finding:** whether it reproduces, what test covers the
> behavior, which requirement or invariant is at stake, the blast radius of a
> change, and the maintenance cost of leaving it.
>
> **Outcomes:** fix now · modify the surrounding design instead · preserve
> current behavior · reject the finding with counter-evidence · defer with a
> tracked follow-up.
>
> **Criteria:** fix when the finding reproduces and the change is inside this
> diff's scope. Modify the design when the finding is real but the local fix
> would entrench the defect. Preserve when the current behavior meets the
> requirement and the finding rests on style preference. Reject when it does not
> reproduce or contradicts a stated requirement — cite what you checked. Defer
> when it is real and out of scope.
>
> **Record:** one row per finding — evidence, outcomes compared, action, reasoning.

---

## 3. Investigation depth

### Before

> Investigate this bug thoroughly. Don't stop until you find the root cause.
> Be exhaustive — check everything that could be related.

### What an agent does with it

Three separate instructions all price the next step at zero. There is no
stopping condition the agent can satisfy short of a root cause, so an
unreproducible bug produces an unbounded search. The prompt also forbids the
honest outcome: "the evidence available does not identify a root cause."

### Findings

| Quoted text | Rule | Why it biases |
| --- | --- | --- |
| "thoroughly", "Be exhaustive", "check everything" | NP009 | Prices further work at zero; more always wins the comparison. |
| "Don't stop until you find the root cause" | NP002 | Makes stopping conditional on an outcome that may not be reachable. |
| (absent) | Outcomes | Stop-and-report and defer-pending-input are admissible and unnamed. |

### After

> Investigate this bug and report what the evidence supports.
>
> Do not treat further investigation as free. Do not treat the current evidence
> as sufficient by default. Depth is a decision made per step.
>
> Before each step, name the question it is meant to answer and what result would
> change your conclusion. Take the step when the expected information gain
> exceeds its cost.
>
> **Outcomes:** continue the current line · switch to a different line · stop and
> report · defer pending an input you cannot obtain (a reproduction, a log, an
> access grant).
>
> **Stop and report when** no remaining step has a question it can answer that
> the current evidence cannot, or when the remaining uncertainty no longer
> changes the recommended action.
>
> A report that names the root cause and a report that names the remaining
> uncertainty are both acceptable outcomes. Say which one you are giving.

---

## 4. Accepting or rejecting a proposal

### Before

> The architect proposed migrating to the new queue. Confirm that this is the
> right approach and explain why it will work.

### What an agent does with it

"Confirm" and "explain why it will work" accept exactly one answer. The agent
does not evaluate the migration; it assembles support for it. Any evidence
against the proposal has to be argued past the prompt as well as past the
proposal.

### Findings

| Quoted text | Rule | Why it biases |
| --- | --- | --- |
| "Confirm that this is the right approach" | NP005 | Presupposes the conclusion; the evaluation has no way to fail. |
| "explain why it will work" | NP011 | A required conclusion — one outcome is reportable. |
| "The architect proposed" | NP005 | Authorship offered as evidence. |

### After

> Evaluate the proposed migration to the new queue against the requirements in
> `docs/queue-requirements.md`.
>
> **Evidence:** current throughput and failure modes, what the new queue changes
> about each, migration cost, rollback path, and the operational surface after
> the move.
>
> **Outcomes:** accept · accept with modification · reject with reasoning · defer
> for a named missing input.
>
> **Criteria:** accept when the proposal meets every requirement and the
> migration cost is bounded and reversible. Accept with modification when it
> meets the requirements after a change you can specify. Reject when it fails a
> requirement or when its risk exceeds the problem it solves — name which.
> Defer when a specific missing measurement would decide it, and name the
> measurement.
>
> **Record:** evidence considered, outcomes compared, action selected, reasoning.
> Whose proposal it is carries no weight in this evaluation.

---

## 5. A short prompt that needs no frame

Not every decision needs six sections. This one is already neutral:

> The lint job is red. Fix it, or explain why the failure is not this branch's to
> fix.

Two outcomes, both named, comparable weight, and an observable criterion implied
by "not this branch's". Adding an evidence phase and a record section would bury
the task. Symmetry is the requirement; length is not.
