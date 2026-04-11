# DeepResearch Prompt 2

## Topic

Function calling / tool use paper audit:

**Can `execution-feedback posterior distillation` be defended as a real method contribution under a strictly fair feedback budget, or does it collapse into teacher leakage / hindsight with more information?**

## Recommended Use

把下面整段直接给 GPT DeepResearch。目标不是找新方向，而是严审当前 thesis 里最脆弱的一环，并产出可执行的实验审查结论。

---

You are acting as a **hostile but technically rigorous NeurIPS reviewer + experimental auditor**.

I am evaluating a function-calling / tool-use paper direction. The paper's main thesis is:

- learn a `schema-abstracted decision representation`
- use `execution-feedback posterior distillation` to refine the decision layer
- prove the thesis with a `schema-invariant evaluation protocol`

The paper is **not** trying to build a large agent framework. It must remain a focused function-calling / tool-use project.

The current method claim is:

1. function calling should be modeled as
   - high-level decision: `p(d | s, T)`
   - schema-conditioned grounding: `p(y | d, s, T)`
2. execution feedback should refine the **decision posterior** rather than only repair surface tool-call tokens
3. the key evidence should come from schema variation and counterfactual decision reuse

Current concern:

The weakest claim is claim 2. A reviewer may say:

> your posterior teacher sees more information than token-level hindsight, so the gain may come from extra supervision rather than from a better learning object.

I want you to audit this issue as strictly as possible.

## Existing Context You Should Assume

Current main direction:

- `A` = main method: schema-abstracted decision representation + execution-feedback posterior distillation
- `B` = evidence chain / evaluation protocol, not a separate method
- `C` = optional extension, currently deprioritized

Already accepted from prior analysis:

- `counterfactual decoding` is essential, not optional
- strongest version is:
  - randomized unseen schema swap
  - fixed decision representation
  - schema-only intervention at decode time
  - `shuffle` and `null` controls on `d`
  - `CF-Gap`
- do **not** redefine the main evidence as “swap grounding head”

Current draft defines a layered feedback budget:

- `Level A`: executable / non-executable flag + coarse error type
- `Level B`: Level A + compressed tool-result summary
- `Level C`: Level B + user correction

But these levels are still provisional and may be unfair or poorly specified.

## Your Task

Please answer the following in a concrete, implementation-facing way.

### Part 1: Identify all leakage channels

List all ways in which a `posterior teacher q(d | s, f)` may receive unfair information relative to a token-level hindsight baseline.

I want you to separate at least these categories:

- information about whether the call executed
- information about whether the call was semantically correct
- direct exposure to correct argument values
- direct exposure to tool outputs that implicitly reveal the correct decision
- access to future dialogue turns / user corrections
- access to evaluator artifacts or hidden labels
- architecture-induced leakage, where the posterior path is simply stronger than the token baseline for reasons unrelated to the thesis

For each leakage channel, explain:

- why it threatens the paper's claim
- whether it is fatal, tolerable, or can be neutralized by protocol design

### Part 2: Define the strictest fair feedback budget

Propose a **precise and minimal** feedback-budget hierarchy for comparing:

- decision-level posterior distillation
- token-level hindsight / repair baseline

I do **not** want a vague discussion. I want a table that specifies, for each budget level:

- what inputs are allowed
- what inputs are forbidden
- what preprocessing / compression is allowed
- whether the level is acceptable for the main paper claim, auxiliary only, or too weak / too leaky

Please revise or replace the current `Level A / B / C` if needed.

Important:

- The decision-posterior method and the token-hindsight baseline must receive **exactly the same information content**
- If equal raw inputs still create unequal effective supervision, explain why and how to fix it

### Part 3: Judge whether claim 2 is actually defensible

Given current literature around function calling, tool use, hindsight fine-tuning, RL for tool use, verifier-style repair, and feedback-conditioned learning:

1. Is “posterior distillation at the decision layer” meaningfully different from token-level hindsight if both are run under the same budget?
2. Under what conditions would reviewers likely accept that difference as novel and important?
3. Under what conditions would reviewers likely reject it as “same recipe in another latent space”?

Be blunt. I want the likely reviewer attack lines, not optimistic wording.

### Part 4: Design the fairest comparison protocol

Design the **minimum convincing experiment matrix** for claim 2.

The matrix must answer all of these:

- is the gain just because the teacher sees more information?
- is the gain just because latent modeling acts like extra capacity?
- is the gain just because token hindsight baseline is underpowered?
- is the gain preserved under schema perturbation / counterfactual reuse?

Please include:

- minimum set of baselines
- minimum set of feedback budgets
- minimum set of datasets / benchmark slices
- which comparisons belong in the pilot and which belong in the final main table

The answer should prefer the **smallest fair matrix**, not a maximal one.

### Part 5: Feedback-conditioned counterfactual decoding

Earlier analysis concluded that counterfactual decoding is already the core evidence for claims 1 and 3.

Now I want you to answer whether claim 2 also needs a **feedback-conditioned counterfactual** variant.

Specifically:

- after producing feedback under schema A, can we compare decision-posterior update vs token-hindsight update under schema transfer to B?
- what is the cleanest protocol for this?
- is this necessary for the paper, or only a strengthening experiment?
- what exact control experiments are needed to make this evidence believable?

### Part 6: Final recommendation

Give a final verdict in this format:

1. `Main-claim-safe`
2. `Main-claim-safe-but-narrow`
3. `Only-safe-as-secondary-claim`
4. `Too-weak-without-RL`
5. `Not-defensible`

Then explain:

- the strongest defensible version of claim 2
- the strongest version that should **not** be claimed
- the single most important experiment I should run next

## Constraints

- Stay inside `function calling / tool use`; do not expand into general agent frameworks
- Do not propose large integrated systems
- RL is allowed only as a comparison axis; do not assume the thesis must depend on RL unless the evidence forces that conclusion
- Be explicit when a point is an inference rather than something directly supported by literature
- Prefer primary sources or authoritative papers when discussing prior work

## Output Format

Please structure the report as:

1. Executive verdict
2. Leakage audit table
3. Recommended feedback-budget table
4. Fair comparison protocol
5. Need for feedback-conditioned counterfactual decoding
6. Reviewer attack lines
7. Concrete changes I should make to the current paper draft

The report should be critical, concrete, and experiment-facing.

Do not spend tokens generating new research ideas. Focus on auditing this exact issue.
