# The decision record

The deliverable that makes a neutral prompt enforceable. Without it, a prompt
that names four outcomes gets an answer that names one, with no way to tell
whether the other three were considered or never read.

A prompt requires the record. It does not require the conclusion.

## Format

Four fields, in this order:

```
Evidence      What you examined, and what it showed. Sources, not summaries:
              file paths, output excerpts, test names, timings, counts.
Alternatives  The outcomes you compared, each with the argument for it and the
              reason it lost — including the one you selected.
Action        The outcome selected, in the vocabulary the prompt used
              (proceed, stop, modify, preserve, accept, reject, defer).
Reasoning     What connects the evidence to the action. Name the criterion that
              decided it and the uncertainty that remains.
```

Keep it proportional. A reversible one-line decision gets one line per field. An
irreversible or expensive decision gets the full trace.

## When to require it

Require the record when the decision is expensive to reverse, when it commits
budget, when it is one of many parallel decisions a reviewer will need to audit,
or when the agent is choosing on the author's behalf without a checkpoint.

Skip it when the decision is cheap, local, and immediately visible in the diff.
A record attached to every trivial choice trains the reader to skip records.

## Worked record

Sub-agent disposition, from the lifecycle example:

```
Evidence      agent-3 last posted 12 minutes ago (status: running, step 4/9).
              Its remaining steps target src/billing/*.ts. The report already
              contains 6 findings covering src/billing/invoice.ts and
              src/billing/tax.ts — the two files its steps 5-9 would read.
              Its steps 4 and 6 target src/billing/refund.ts, which no
              completed agent has reported on.
Alternatives  Continue: reaches refund.ts, which is uncovered. Cost ~6 min of
              the 15-min budget.
              Consume and stop: keeps the 6 landed findings, loses refund.ts
              coverage entirely.
              Stop as redundant: rejected — scope is not fully covered.
              Defer: rejected — one more output would land in invoice.ts,
              which is already covered, so it would not settle anything.
Action        Continue.
Reasoning     Criterion met: remaining scope covers a file no completed agent
              has reported on (refund.ts). The 6-minute cost fits the budget.
              Uncertainty: if step 4 finds nothing in refund.ts, steps 5-9 are
              redundant and the agent should be stopped at that point.
```

The record makes the *next* decision cheaper: the uncertainty line names the
condition under which the choice flips.

## Grading a record

A record is complete when a reader who disagrees with the action can say exactly
where they disagree — at the evidence, at the comparison, or at the criterion.

Four failure modes:

1. **Evidence that is a summary.** "The agent was still producing useful output"
   is a conclusion. "Its last three outputs restated findings already in the
   report" is evidence.
2. **Alternatives listed but not compared.** Naming the other outcomes without
   the reason each lost is a checkbox, not a comparison.
3. **A criterion invented after the fact.** The criterion should be the one the
   prompt supplied. When the agent had to invent one because the prompt left it
   out, the record says so — that is a finding about the prompt.
4. **Uncertainty dropped.** A record with no remaining uncertainty is usually a
   record with unexamined uncertainty. Say what would change the answer.

## Recording a deferral

`defer` is a real outcome and gets a real record. A deferral that does not name
what it is waiting for is a stop wearing a softer word:

```
Action        Defer.
Reasoning     Deciding requires the p99 latency of the new queue under
              production load. The staging measurement does not transfer —
              staging runs 1/40th the volume. Blocked on the load test
              scheduled for Thursday. If it does not run by Friday, the
              decision falls back to reject on cost grounds.
```

Name the missing input, why the available evidence cannot substitute, and what
happens if the input never arrives.
