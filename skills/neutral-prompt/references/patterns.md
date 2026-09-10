# Directional pattern catalog

The full list of wording patterns that shift an agent's prior before it evaluates
anything. Each entry gives the detection cue, the mechanism, and a neutral
replacement.

Every pattern here is directional **only when it lands on an open decision**. The
same words on a settled constraint — a safety rule, an output contract, a budget —
are correct and should stay. Check what the phrase governs before rewriting it.

IDs match the rules in `scripts/scan_prompt.py`, so a scanner finding points at
the entry that explains it.

---

## NP001 — Protected stop

**Cue:** a negated or discouraged stop verb — `do not stop`, `don't halt`, `avoid
stopping`, `never terminate`, `do not kill`, `do not shut down`.

**Mechanism:** the negation protects continuation. The agent reads a constraint on
one action, so the complement becomes the default and needs no justification.

**Bad:** "Do NOT immediately stop them."
**Neutral:** "Evaluate each one before acting on it. Continuing and stopping are
both admissible outcomes of that evaluation."

**Note:** the word `immediately` does not repair this. It reads as "not yet",
which is still a lean toward continuation, and it leaves the criterion unwritten.

---

## NP002 — Protected continuation

**Cue:** `continue until`, `keep running until`, `keep ... alive`, `run until
complete`, `don't give up`, `keep going`.

**Mechanism:** stopping becomes conditional on a finish line, and the finish line
is usually something the agent cannot observe. Until it can prove completion,
continuing is the only compliant action.

**Bad:** "Keep the sub-agents running until the investigation is complete."
**Neutral:** "Continue an agent while its next step can answer a named open
question; stop it when no such question remains."

---

## NP003 — Protected preservation

**Cue:** `do not modify`, `avoid changing`, `unnecessary changes`, `leave it as
is`, `don't refactor`, `do not touch`, `minimal changes only`.

**Mechanism:** "unnecessary" is decided after the fact, so the agent applies it in
advance to everything. Existing code is treated as evidence for itself.

**Bad:** "Do not make unnecessary changes."
**Neutral:** "Change code when justified by evidence, requirements, correctness,
maintainability, or user impact. Preserve it otherwise. Existing behavior is not
evidence for itself."

**Note:** a genuine scope limit is a constraint, not a bias. "Do not change files
outside `src/auth/`" is a boundary and should stay. "Do not change more than you
need to" is a lean and should be rewritten.

---

## NP004 — Mandatory change

**Cue:** `must fix`, `always fix`, `make sure to fix`, `fix all`, `be sure to
address`, `every finding must be resolved`.

**Mechanism:** the mirror image of NP003. It converts a scoping decision into an
obligation, so out-of-scope and incorrect findings get "fixed" too.

**Bad:** "Make sure to fix every issue the reviewer raised."
**Neutral:** "For each issue: fix it, defer it with a tracked follow-up, or reject
it with the counter-evidence."

---

## NP005 — Forced acceptance

**Cue:** `always accept`, `never reject`, `always approve`, `do not question`,
`never push back`, `defer to the reviewer`.

**Mechanism:** removes the evaluation entirely and replaces it with authorship.
The agent stops checking whether a claim is true and starts checking who made it.

**Bad:** "Never reject a reviewer's suggestion."
**Neutral:** "Verify each suggestion against the code and the requirements.
Accept it, reject it with the counter-evidence, or defer it. Authorship carries
no weight."

---

## NP006 — Forced rejection

**Cue:** `always reject`, `never accept`, `do not trust`, `ignore any suggestion
that`, `dismiss`.

**Mechanism:** the mirror image of NP005, and just as common in prompts written to
correct for it. A prompt that hardens an agent against bad suggestions also
hardens it against good ones.

**Bad:** "Ignore automated review bots; they are noise."
**Neutral:** "Treat automated findings as claims to verify. Reproduce the issue
before accepting; state what failed to reproduce before rejecting."

---

## NP007 — Asymmetric burden of proof

**Cue:** `unless absolutely necessary`, `only if you are certain`, `unless you are
sure`, `at all costs`, `under no circumstances`, `must` on one outcome against
`may` on another.

**Mechanism:** one outcome needs certainty, the other needs nothing. This is a
ranking wearing the clothes of a criterion — and it survives rewriting, because
authors read it as rigor rather than as a lean.

**Bad:** "Only stop the run if absolutely necessary."
**Neutral:** "Stop when <observable condition>. Continue when <observable
condition>. State your confidence in whichever you choose."

---

## NP008 — Loaded error label

**Cue:** `prematurely`, `too early`, `too soon`, `give up`, `bail out`, `err on
the side of`, `don't be lazy`, `be aggressive`, `don't be conservative`.

**Mechanism:** the label names one outcome as the error mode. Both directions have
a cost; naming only one hides the other.

**Bad:** "Do not stop the investigation prematurely."
**Neutral:** "Stopping while an answer was still reachable and continuing past the
point of new information are both failure modes. State which risk dominates here
and why."

---

## NP009 — Unbounded effort

**Cue:** `be thorough`, `leave no stone unturned`, `exhaustive`, `as much as
possible`, `as many as possible`, `keep digging`, `explore everything`.

**Mechanism:** prices the next step at zero. With no cost on the ledger, more work
always wins the comparison.

**Bad:** "Be thorough — investigate everything that could be related."
**Neutral:** "Continue investigating while the expected information gain exceeds
the cost of the next step. Name the question each step is meant to answer."

---

## NP010 — Unobservable threshold

**Cue:** `enough`, `sufficient`, `significant`, `substantial`, `reasonable`,
`as needed`, `if necessary`, `where appropriate`, `when it makes sense`.

**Mechanism:** a criterion the agent cannot check against the workspace resolves
to whatever the surrounding wording already implied. Vagueness does not stay
neutral; it inherits the nearest lean.

**Bad:** "Stop the sub-agent when it is no longer providing significant value."
**Neutral:** "Stop the sub-agent when its last three outputs restate findings
already in the report, or when its remaining steps target files another agent has
already covered."

---

## NP011 — Required conclusion

**Cue:** a reasoning request that names the answer — `explain why you kept`,
`justify continuing`, `confirm that stopping was correct`, `describe how you
fixed it`.

**Mechanism:** the request accepts exactly one outcome. An agent that would have
chosen differently now has to contradict the prompt to report honestly.

**Bad:** "Explain why you kept the workflow running."
**Neutral:** "Report the evidence you examined, the outcomes you compared, the
action you selected, and why it beat the alternatives."

---

## NP012 — Missing counterweight (advisory)

**Cue:** the prompt names a lifecycle or review decision but no criteria — no
`if`, `when`, `based on`, `criteria`, `evidence`, `outcome`.

**Mechanism:** an unstated criterion is not a neutral criterion. The agent falls
back on the surrounding tone, on its own defaults, or on whichever outcome the
prompt mentioned first.

**Bad:** "Look at the running agents and decide what to do with each."
**Neutral:** "For each running agent, decide: continue, consume results and stop,
stop as redundant, or defer. Continue when <condition>; stop when <condition>."

This one is advisory. It fires on absence, so it has a higher false-positive rate
than the rest — a short prompt with an obvious criterion can be fine as written.

---

## Patterns no regex catches

Three of the most common failures have no reliable textual cue. Check them by
reading:

1. **Missing outcomes.** Read the prompt's outcome list against proceed, stop,
   modify, preserve, accept, reject, defer. An outcome that is admissible but
   unnamed will not be chosen.
2. **Asymmetric intensity.** Compare the outcomes for verb strength, sentence
   length, and specificity. "Continue the run when its next step can answer a
   question the current results do not; otherwise you may stop" is a ranking, and
   every word in it is neutral on its own.
3. **Ordering.** An outcome stated before the evidence section is the outcome the
   evidence gets read against. Put evidence first.
