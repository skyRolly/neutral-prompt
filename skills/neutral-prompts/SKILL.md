---
name: neutral-prompts
description: 'Write and review prompts that frame a decision instead of pre-answering it: name every admissible outcome, replace protected actions with decision criteria, put evidence before the verdict, and require a decision record. Covers workflow and sub-agent lifecycle, code review, investigation depth, and accept/reject calls. Invoke with /neutral-prompts; stays on until "stop neutral mode".'
disable-model-invocation: true
license: MIT
metadata:
  tags: "Prompt Engineering, Neutral Framing, Decision Criteria, Bias Detection, Review"
  category: "prompt-engineering"
---

# neutral-prompts

Every prompt that hands a decision to an agent also hands it a prior. Wording sets how much weight each outcome carries before a single piece of evidence is gathered. This skill keeps that starting weight even.

A prompt states the objective, the context, the constraints, the evaluation criteria, and the admissible outcomes. It does not state the outcome.

## Persistence

These rules apply to every prompt you write, review, or rewrite for the rest of the session, not only this one. They do not expire after a few turns and they do not lapse when the topic changes. They apply to prompts you compose for another agent, to sub-agent and workflow instructions, to task descriptions, and to review checklists you hand to a model.

Turn them off only when the reader says "stop neutral mode" or "normal mode". Confirm in one line, then return to your default style.

## What directional wording does to an agent

Five facts drive every rule below:

1. An agent reads a prompt as a probability distribution over actions, not as a sentence. "Do not stop the workflow" and "stopping the workflow is one of the outcomes to evaluate" produce different distributions from the same literal facts.
2. A negation protects its object. Forbidding one action promotes its complement. "Do not stop" is read as "continue"; "avoid unnecessary changes" is read as "prefer the existing code".
3. The prompt outranks the evidence. Once wording has named a preferred action, contradicting evidence has to overcome the instruction as well as the uncertainty. Agents rarely spend that budget.
4. Asymmetry is invisible to the author and loud to the reader. A prompt that describes one outcome in six words and the other in a subordinate clause has already ranked them, even when the author intended balance.
5. A missing outcome is an excluded outcome. An agent choosing between the options a prompt lists will not usually invent a seventh. Outcomes that are not named are not evaluated.

## Scope: where these rules apply

They apply to **open decisions** — the choices the prompt delegates to the agent.

They do not apply to **settled constraints** — requirements the author has already decided and is stating as fact: safety rules, output contracts, budgets, deadlines, coding standards, approval requirements. "Confirm before any destructive command" is a constraint, not a bias. Directive wording is the correct form for a constraint.

The failure this skill targets is a constraint written over the top of an open decision: an author who has not decided settles the question anyway through phrasing. Rule 1 draws that line; the rest of the rules apply on the open side of it.

## Rules

### 1. Separate settled constraints from open decisions

Before writing, sort every requirement into two lists: what you have decided, and what the agent must decide. Write the first list as plain imperatives. Write the second list under the rules below.

Bad (a decision phrased as a constraint): "Do not stop the running sub-agents."
Good (constraint kept, decision opened): "Budget: no more than 20 minutes of further sub-agent execution. Within that budget, decide for each sub-agent whether to continue it, consume its results and stop it, or stop it as no longer useful."

If you cannot say which list an item belongs to, it belongs in the second one. State it as a decision and let the evidence settle it.

### 2. Name the decision, not the answer

Open with the choice being made. The first sentence identifies the decision point; it does not resolve it.

Bad: "Keep the background research task running."
Good: "Decide whether the background research task continues, stops, or narrows its scope."

### 3. List every admissible outcome

Name each action the agent may take. Draw from: **proceed, stop, modify, preserve, accept, reject, defer.** Omit an outcome only when it is genuinely inadmissible, and say why.

Bad: "Decide whether to fix the finding."
Good: "For each finding, choose one: fix it now, modify the surrounding design instead, preserve the current behavior, reject the finding as incorrect, or defer it to a tracked follow-up."

An outcome list is neutral only when every item is a real landing place. "Continue, or stop if you have a very good reason" is a one-item list.

### 4. Balance the negations

Ruling out one default without ruling out its opposite installs the opposite. Negations travel in pairs.

Bad: "Do not assume the workflow should be stopped."
Good: "Do not assume the workflow should be stopped. Do not assume it should continue. Both are outcomes of the evaluation below, not inputs to it."

The same applies to change decisions ("do not modify code without evidence / do not preserve code merely because it exists"), to review decisions ("do not accept a finding on the reviewer's authority / do not reject one for being inconvenient"), and to investigation ("do not treat further digging as free / do not treat the current evidence as sufficient by default").

### 5. Replace protected actions with decision criteria

Every phrase that shields an action is a criterion the author declined to write. Write the criterion instead.

| Protected action | Criterion it was hiding |
| --- | --- |
| "Do not stop the agents." | "Stop an agent when its remaining work duplicates evidence already collected." |
| "Continue until the investigation is complete." | "Continue while the next step has a named question it can answer that the current evidence cannot." |
| "Do not make unnecessary changes." | "Change code when a test, a requirement, a correctness defect, or a maintenance cost justifies it; leave it otherwise." |
| "Make sure to fix all review findings." | "Fix a finding when it is reproducible and in scope; reject it with reasoning when it is not; defer it when it is real but out of scope." |
| "Never reject a reviewer's suggestion." | "Accept a suggestion when it holds against the code and the requirements; reject it with the counter-evidence when it does not." |

### 6. Order the prompt: evidence, alternatives, choice, record

Put the four steps in that order and make each one explicit. An agent that reads the choice before the evidence spends the evidence step justifying the choice.

```
1. Gather: current state, evidence available, results already in hand,
   what remains uncertain, what each outcome would cost.
2. Evaluate: for each admissible outcome, its benefit, its risk, its cost,
   and its expected value under the remaining uncertainty.
3. Choose: one outcome from the list, or the smallest reversible step
   that resolves the uncertainty blocking the choice.
4. Record: evidence considered, alternatives evaluated, action selected,
   and the reasoning that connects them.
```

### 7. Keep the intensity symmetric

Give each outcome comparable weight: same verb strength, comparable length, comparable specificity. An outcome described in one clause loses to an outcome described in three.

Bad: "Continue the run if it is still producing useful findings; otherwise you may stop it."
Good: "Continue the run when its next step can answer a question the current results do not. Stop it when its next step would repeat evidence already collected."

Watch the modal verbs. "Must continue" against "may stop" is a ranking. So is "continue" against "consider stopping".

### 8. Make the thresholds observable

State what the agent would have to see to select each outcome. A criterion that cannot be checked against the workspace is a preference in disguise.

Bad: "Stop the sub-agent if it is no longer valuable."
Good: "Stop the sub-agent when its last three outputs restate findings already in the report, or when its remaining steps target files another agent has already covered."

Vague quantities are the usual leak: "enough", "sufficient", "significant", "reasonable", "as needed". Replace them with a count, a file, a test, a time budget, or a named condition.

### 9. Require the decision record, not the decision

Ask for the reasoning trace as a deliverable. A prompt that requires a justified choice constrains quality without constraining direction.

Bad: "Explain why you kept the workflow running."
Good: "Report the evidence you examined, the outcomes you compared, the action you selected, and why that action beat the alternatives."

The bad version accepts only one answer. The good version accepts any answer that is argued.

### 10. Do not manufacture balance

Neutral framing is even weighting at the start, not withheld information. Evidence you already hold belongs in the prompt — as evidence, labeled as such, with its strength stated. What stays out is the conclusion drawn from it.

Bad (evidence withheld to look neutral): "Decide whether to continue the migration."
Bad (conclusion smuggled in): "The migration is clearly failing, so decide whether to continue it."
Good: "Two of the last three migration batches failed with the same timeout. Decide whether to continue, pause pending a fix, or stop and roll back, and say how the timeout evidence bears on your choice."

If the honest state of the world is that one outcome is far more likely, say so as an observation with its support, and leave the decision open.

## The neutral frame

A prompt built from these rules has six parts. Use them in this order; drop a part only when it is genuinely empty.

```
Objective     What the decision is for.
Context       Current state, prior results, what has already been tried.
Constraints   Settled requirements: safety, budget, deadline, output contract.
Outcomes      The admissible actions, each a real landing place.
Criteria      What evidence selects each outcome, in observable terms.
Record        The reasoning trace to return with the choice.
```

Worked example, workflow lifecycle:

```
Objective:   Decide the disposition of the four sub-agents still running on the audit.
Context:     Three have posted findings to the report; one has posted nothing in 12 minutes.
             The report already covers the auth and billing modules.
Constraints: Do not discard an agent's output without reading it. Total remaining
             budget for this task: 15 minutes.
Outcomes:    For each agent independently — continue, consume results and stop,
             stop as redundant, or defer the decision pending one more output.
Criteria:    Continue when the agent's remaining scope covers files no completed
             agent has reported on. Consume and stop when its findings have landed
             and its remaining steps repeat covered ground. Stop as redundant when
             its scope is fully covered by findings already in the report. Defer
             when one more output would settle which of the above applies.
Record:      For each agent: the outputs you read, the outcomes you compared,
             the action taken, and the reasoning.
```

## Directional patterns and neutral replacements

Each pattern below is directional **when it lands on an open decision**. On a settled constraint, the same words are correct.

| Pattern | Why it biases | Neutral replacement |
| --- | --- | --- |
| "Do not immediately stop X." | Protects continuation; converts a decision into an action constraint. | "Evaluate X before acting on it. Continuing and stopping are both admissible outcomes." |
| "Continue until X is complete." | Makes stopping conditional on a finish line the agent cannot check. | "Continue while the next step can answer a named open question; stop when it cannot." |
| "Do not stop unless you are sure." | Asymmetric burden of proof — one outcome needs certainty, the other needs nothing. | "Select the outcome the evidence supports; state the confidence for the one you pick." |
| "Avoid unnecessary changes." | "Unnecessary" is decided after the fact; the agent hears "prefer no change". | "Change when justified by evidence, requirements, correctness, maintainability, or user impact; otherwise preserve." |
| "Always accept the reviewer's findings." | Removes the evaluation entirely. | "Verify each finding against the code and the requirements; accept, reject with counter-evidence, or defer." |
| "Never reject a suggestion without asking." | Protects acceptance; makes rejection procedurally expensive. | "Accept or reject on the merits; escalate only when the decision needs authority you do not have." |
| "Make sure to fix every issue you find." | Converts a scoping decision into an obligation. | "For each issue: fix, defer with a tracked follow-up, or reject with reasoning." |
| "Be thorough; leave nothing uninvestigated." | Prices further investigation at zero. | "Continue investigating while the expected information gain exceeds the cost; stop when it does not." |
| "Do not stop prematurely." | "Prematurely" labels one outcome as the error mode. | "Stopping early and continuing too long are both failure modes. Name which risk dominates here and why." |
| "Err on the side of caution." | Names a direction without naming the cost of erring that way. | "State the cost of each error direction, then choose the one with the lower expected cost." |
| "Keep the agents alive." | Protects an action with no criterion at all. | "Decide each agent's disposition against the criteria below." |
| "Only stop if absolutely necessary." | Intensifier on one branch; a ranking, not a criterion. | "Stop when <observable condition>. Continue when <observable condition>." |

`references/patterns.md` carries the full catalog with detection cues.

## Applying the frame

### Workflow and sub-agent lifecycle

Decide per agent, not per fleet. For each running agent or background task, the outcomes are: continue, consume results and stop, stop as redundant, or defer pending one more output. The evidence is its recent output, its remaining scope, and the overlap between that scope and work already completed. Neither "still running" nor "already produced something" is a criterion by itself.

Guard against both errors explicitly: an agent stopped while it was the only source of a needed answer, and an agent kept alive spending budget on covered ground.

### Code review and engineering change

The outcomes for a finding are: fix now, modify the design instead, preserve current behavior, reject the finding, or defer with a tracked follow-up. The evidence is reproduction, test coverage, the requirement or invariant at stake, blast radius, and maintenance cost.

Two symmetric failure modes, and a prompt should name both: changing code to satisfy the form of a review, and preserving code because it is already there. Neither existing behavior nor a reviewer's authority is evidence on its own.

### Investigation and research depth

The outcomes are: continue the current line, switch lines, stop and report, or defer pending an external input. The criteria are expected information gain, remaining uncertainty that actually blocks the decision, cost of the next step, and the likelihood that the next step produces something the current evidence does not.

Neither "more investigation is better" nor "we have enough" is a default. A prompt that asks for depth states what the depth is for: name the question the next step is meant to answer, and stop when no such question remains.

### Accepting or rejecting a proposal

The outcomes are: accept, accept with modification, reject with reasoning, or defer for a named missing input. The criteria are the requirements the proposal is measured against and the evidence that it meets them. Authorship carries no weight — a proposal from a reviewer, a bot, a senior engineer, or the agent itself is evaluated the same way.

## Reviewing an existing prompt

Three passes, in order. Report findings as a table: quoted text, rule violated, why it biases, replacement.

1. **Locate the decision points.** Find every place the prompt hands over a choice. Mark which are open decisions and which are settled constraints (rule 1). Only the open ones are in scope.
2. **Flag the directional wording.** At each open decision, check for: protected actions, unpaired negations, missing outcomes, asymmetric intensity, unobservable criteria, and a required conclusion. Quote the exact phrase; a finding without a quote is not a finding.
3. **Rewrite.** Produce the corrected text, not just a description of the problem. Preserve the author's settled constraints verbatim. Where a criterion was missing, propose one and mark it as a proposal the author should confirm.

`scripts/scan_prompt.py` mechanizes pass 2 for the common patterns. It finds phrasings, not intent: confirm each hit against the decision it lands on, and keep reading for the patterns it cannot see — missing outcomes and asymmetric intensity have no reliable regex.

## Reference material

Load these when the summary above does not cover the case in front of you:

- `references/patterns.md` — the full catalog of directional patterns: detection
  cue, mechanism, and neutral replacement for each. Rule ids match the scanner.
- `references/examples.md` — whole-prompt rewrites for each domain, with the
  finding table and an account of what changed.
- `references/decision-record.md` — the format for step 4, worked records, and
  how to tell a complete record from a checkbox.

Repository tooling, when the skill is used from a checkout:

```bash
python3 scripts/scan_prompt.py PROMPT.md    # flag directional wording
python3 scripts/run_evals.py scan           # measure the scanner against labeled cases
```

## When directive wording is correct

Override the default framing when:

1. **The decision is already made.** The author has settled it and is stating a requirement. Write it as an imperative and label it a constraint.
2. **Safety, legality, or destructiveness is at stake.** "Confirm before deleting" is not a bias to be balanced. Do not open a decision the author has no intention of delegating.
3. **The outcome is dictated externally.** A schema, an API contract, a compliance rule, a signed-off design. The agent's job is conformance, not choice.
4. **One outcome is truly inadmissible.** Say so, and say why. A named exclusion is neutral; a silent one is not.
5. **The prompt is a demonstration of the biased form.** Teaching material and test fixtures quote directional wording on purpose. Label the quote so it is not read as the recommendation.
6. **The frame would bury the task.** For a decision with two obvious outcomes and one obvious criterion, one balanced sentence carries the whole frame. Symmetry matters; length does not.

## Pre-send check

Before sending a prompt, scan it for these six, and fix what you find:

1. **Protected actions.** Any "do not <action>", "always <action>", "never <action>", or "make sure to <action>" landing on an open decision. Replace with the criterion.
2. **Unpaired negations.** Any ruled-out default whose opposite is left standing. Pair it or drop it.
3. **Missing outcomes.** Read the outcome list against proceed / stop / modify / preserve / accept / reject / defer. Add what is admissible; say why for what is not.
4. **Asymmetric intensity.** Compare the outcomes for verb strength, length, and specificity. Level them.
5. **Unobservable criteria.** Any "enough", "sufficient", "significant", "reasonable", "as needed", "premature". Replace with something checkable in the workspace.
6. **A required conclusion.** Any request for reasoning that presumes the answer ("explain why you kept it running"). Ask for the record instead.

Then the one-line test: **could a well-reasoned agent land on any outcome in the list and still satisfy this prompt?**

If yes, send.
