# DeepResearch Status

## Current Thesis

Current main thesis:

- Learn a `schema-reusable decision representation`
- Prove it through `counterfactual decoding + d-intervention controls`
- Keep `execution-feedback posterior distillation` out of the current main paper
- Treat `RL` as out-of-scope for the current mainline

Current positioning:

- `A` is now only `cross-schema decision reuse`
- `B` is the core evidence chain / falsification protocol
- `claim 2 / EFPD` is now explicitly `phase-2 secondary claim`
- `C` remains deprioritized

## Completed Research

### Prompt 0: General harsh review / restructuring

Output file:

- `docs/archive/reviews/面向NeurIPS2026 的 Function Calling 立项严审与重构报告.pdf`

Main conclusions:

- The core thesis is valid, but novelty is fragile unless it is formalized as `decision invariant / grounding equivariant`
- The biggest danger is being interpreted as `CoLA adaptation + token hindsight in another space`
- `B` should not be a second independent contribution; it should be the protocol that makes `A` falsifiable
- `C` should not be the main line
- BFCL should be used mainly for evaluation, not as the main training source

### Prompt 1: Counterfactual decoding protocol

Output file:

- `docs/archive/reviews/Counterfactual Decoding 在 Schema-Abstracted Tool Use 论文中的定义与证据强度评估.pdf`

Main conclusions:

- `Counterfactual decoding` is not an optional diagnostic; it is a core evidence protocol
- The strongest version is:
  - randomized unseen schema-swap
  - fixed decision representation
  - schema-only intervention
  - `d`-intervention controls (`shuffle` and `null`)
  - `CF-Gap` as an auxiliary metric
- It is not enough to show cross-schema robustness; the paper must show that the same decision representation can be reused under schema intervention
- Without this protocol, the paper collapses toward:
  - stronger augmentation / masking
  - stronger robustness recipe
  - CoLA-style latent adaptation

### Prompt 2: Feedback budget / teacher leakage

Output file:

- `docs/archive/reviews/执行摘要.pdf`

Main conclusions:

- Prompt 2 confirms that `same-budget` cannot mean only `feedback budget`
- for claim 2, the paper must also reason about:
  - model capacity budget
  - data budget
  - optimization / FLOPs budget
  - environment interaction budget
  - inference budget
- claim 2 should remain provisional unless these budgets are either matched or explicitly reported
- the current `Level A / B / C` feedback hierarchy is still usable, but:
  - `Level A` is the safest main-table setting
  - `Level B` is acceptable only if the summary/compression rule is fixed and shared
  - `Level C` has the highest leakage risk and should not be default main-claim evidence
- the draft needs explicit statistical reliability requirements:
  - multiple seeds
  - confidence intervals / error bars
  - strict train / eval separation

What we accept from Prompt 2:

- multidimensional same-budget accounting is necessary
- claim 2 wording must stay cautious
- standard distillation and scratch-matched fine-tuning are useful fairness baselines
- statistical reliability requirements need to be stated in the draft

What we do **not** automatically accept as mainline changes:

- `RLHF` as a required primary baseline
- `CoT prompting` as a required primary baseline

Reason:

- both are reasonable sanity checks in some papers, but they do not directly target the core reviewer attack here
- adding them to the main matrix would risk re-expanding the project without materially strengthening the main thesis

### GPT-5.4 Pro: Claim-2 audit

Input materials:

- `/Users/huangyixuan/Documents/tooluse/2026-03-31-nips2026-function-calling-idea-draft-v2.md`
- `docs/superpowers/plans/2026-04-08-schema-reuse-pilot-v1-implementation-plan.md`

Main conclusions:

- `claim 2 / execution-feedback posterior distillation` is currently only safe as a **secondary claim**
- the broad statement
  - `execution feedback should generally refine decision posterior rather than tokens`
  should **not** be claimed
- if claim 2 is ever revived, the strictest defensible version is:
  - under a strictly matched, schema-name-free feedback budget, decision-level distillation improves `A_feedback->B` transfer more than equally informed token-level hindsight
- the minimum fair claim-2 matrix would require:
  - frozen rollout tuples
  - same-information feedback ledger
  - `Decision-NoFB`
  - `Token-Hindsight-Strong`
  - `Latent+Token-Hindsight`
  - `Decision-PD`
  - `A_feedback->B`
  - `shuffle/null` on updated `d`

What we accept from this audit:

- current `v2` narrowing is correct
- claim 2 should stay out of title / abstract / headline contributions
- any future feedback comparison must use a strict runtime-only ledger, not vague `Level A/B/C` language

What we do **not** do now:

- do not pull claim 2 back into `pilot-v1`
- do not expand the current project into a feedback paper
- do not add RL because of claim-2 weakness

### GPT-5.4 Pro: Pilot-v1 core audit

Input materials:

- `/Users/huangyixuan/Documents/tooluse/2026-03-31-nips2026-function-calling-idea-draft-v2.md`
- `docs/superpowers/plans/2026-04-08-schema-reuse-pilot-v1-implementation-plan.md`

Main conclusions:

- verdict: `NOT YET SCIENTIFICALLY SHARP`
- this does **not** kill the current thesis, but it says the current pilot is better at falsifying the thesis than proving it
- the biggest remaining gap is now **identifiability**, not idea sprawl
  - `shuffle/null` proves `d` is used
  - it does not by itself prove `d` is exactly the reusable decision object claimed
- the most serious protocol flaw was:
  - direct baselines do not naturally admit a symmetric fixed-`d` `A->B` comparison
- `G_main` is acceptable for pilot-v1, but only for a narrow claim:
  - reuse under tightly controlled, symbolically bijective schema transforms

Minimal revisions accepted from this audit:

- split evaluation into:
  - `Track R / reuse-identifiability`
  - `Track P / robustness-payoff`
- add a `B->B` interpretability gate
- make `rename+arg` a required pass slice
- elevate `latent-consistency-only` to a hard gate
- remove or soften the slogan:
  - `prove d is not an ordinary compression code`

## What Has Been Updated In The Draft

The current scientific draft at:

- `/Users/huangyixuan/Documents/tooluse/2026-03-31-nips2026-function-calling-idea-draft-v2.md`

has already been updated with:

- `cross-schema decision reuse` as the only main thesis
- `counterfactual decoding + shuffle/null + held-out transforms` as the core evidence chain
- `pilot-v1` reduction to:
  - single-turn
  - audit-aware
  - paired-schema synthetic transforms
  - no EFPD
  - no RL
- explicit `G_main / G_ext / H_robust` separation
- explicit baseline matrix for the no-feedback pilot
- explicit go/no-go thresholds and pivot logic

Additional changes made after GPT-5.4 Pro claim-2 audit:

- claim 2 is now explicitly labeled `secondary claim under strict budget`, not a hidden backup mainline
- the draft now states that future EFPD work would require:
  - same-information budget
  - frozen rollouts
  - matched-latent token baseline
  - `A_feedback->B`
- the draft no longer leaves room for vague “feedback should update decisions” wording

Additional changes made after GPT-5.4 Pro pilot-v1 core audit:

- the pilot is now split into two evaluation questions:
  - `Track R`: does a reusable fixed-`d` object exist
  - `Track P`: does reuse-oriented training outperform direct robustness recipes on held-out target schemas
- direct baselines are no longer assumed to share the same fixed-`d` `A->B` table with reuse_main
- `rename+arg` is now treated as a mandatory gate rather than just a breakdown slice
- `B->B` now has to be interpretable before `CF-Gap` can be used as positive evidence
- the main draft no longer claims that the pilot can prove `d` is not a compression code in the strongest sense

## Current Assessment

The project is still worth pursuing.

But the thesis is only strong if all of the following become true:

1. `decision / grounding` separation is functionally real, not just architecturally present
2. `counterfactual decoding` works under randomized schema transforms
3. `A->B` is clearly above `shuffle/null`
4. the gain survives held-out alias / held-out transform settings
5. the gain is not already explained by augmentation, Hammer-style masking, or plain latent bottlenecks
6. BFCL-based gains remain after sanity-checking noisy subsets

Current biggest risks:

- `d` is still just a compression code
- decoder ignores `d`
- gains are actually due to masking / augmentation effects
- `G_main` may still be too weak and produce only a narrow alias/order robustness story
- direct-vs-reuse protocol asymmetry may still reappear during implementation if `Track R / Track P` are not kept separate
- BFCL slice quality is still not trustworthy enough
- future claim-2 work, if revived, will again collapse into a fairness battle

Most fragile claim right now:

- no longer the current main thesis
- the most fragile **future** claim remains claim 2:
  - `execution-feedback posterior distillation` would still need to beat token-level hindsight under a strict same-information protocol
  - but this is now phase-2 only

## Recommended Next Prompts

Do **not** run more “find new directions / new tricks” prompts.

The next prompts should stay narrow and pilot-facing.

### Priority 1: Pilot-v1 core audit

Why:

- after freezing claim 2, the main uncertainty is no longer feedback fairness
- it is whether the current `pilot-v1` is actually strong enough to prove `decision reuse`

Goal:

- audit `G_main`
- audit the current baseline matrix
- audit whether the gate criteria are hard enough
- decide whether the current pilot is `passable`, `borderline`, or still too weak

Recommended prompt:

- `docs/prompts/gpt54-pro-prompt-pilot-audit.md`

Status:

- completed
- main outcome: keep the thesis, but harden the protocol before implementation

### Priority 2: Benchmark slice trustworthiness

Why:

- BFCL-v3 multi-turn audit risk is still real
- even for single-turn pilot, data slice quality remains a vulnerability

Goal:

- decide the most trustworthy single-turn executable slice
- define what must be manually checked before pilot results are taken seriously

### Priority 3: Implementation of Task 1-5

Why:

- once the pilot design is judged hard enough, the next bottleneck is no longer ideation
- it is building the falsification pipeline

Goal:

- bootstrap repo
- build candidate slice
- build transform engine
- build paired dataset
- build counterfactual evaluator

## What Probably Does NOT Need Another Prompt

These areas are already sufficiently settled for now:

- whether `C` should be the main line: no
- whether the paper should become a big agent framework: no
- whether claim 2 should be dragged back into the current paper: no
- whether more fancy latent / diffusion / reranking ideas should be explored now: no

## Immediate Actionable Questions

Before implementation, the project still needs explicit answers to:

1. What is the exact `counterfactual decoding` implementation?
2. What BFCL subset is trustworthy enough for pilot results?
3. Can `Track R / Track P` be implemented cleanly without protocol leakage?
4. Are the current stop/continue rules already hard enough after the latest patch?

## Immediate Next Move

Recommended sequence now:

1. keep claim 2 frozen as a phase-2 secondary claim
2. integrate the completed pilot-v1 core audit into the draft and implementation plan
3. start executing `Task 1-5`
4. only then reconsider whether another reviewer pass is needed

## Current Recommendation

Next best move:

1. Do **not** open a new feedback / RL research branch
2. Keep the new two-track protocol (`Track R` / `Track P`) intact during implementation
3. Begin implementing the falsification pipeline
4. Only after no-feedback `decision reuse` is established should phase-2 be reopened
