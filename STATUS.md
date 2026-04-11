# STATUS

Last updated: 2026-04-11

## Project thesis

The current paper direction is:

- `cross-schema decision reuse`
- function calling only, not a general agent framework
- no `RL` in the current mainline
- no `execution-feedback posterior distillation` in the current mainline

The core claim to test is whether a decision object learned under schema `T_A` can be reused under an equivalent schema `T_B`, with the main evidence coming from:

- `A->B` counterfactual decoding
- `shuffle/null` controls on `d`
- held-out schema transforms

Primary scientific draft:

- `2026-03-31-nips2026-function-calling-idea-draft-v2.md`

## Current repo state

What is already implemented and locally verified:

- paired-schema data pipeline for the current `pilot_v1` toy slice
- counterfactual evaluation skeleton
- LLaMA-Factory baseline export path for:
  - `vanilla`
  - `schema_augmented`
  - `hammer_like`
- smoke CLI yaml templates for LLaMA-Factory baseline SFT
- environment probe for deciding whether a machine is suitable for real training

Verified commands:

- `python3 -m pytest -q`
  - current result: `18 passed`
- `python3 scripts/export_llamafactory_baselines.py`
  - current result: exports `data/llamafactory/pilot_v1/*` successfully
- `python3 scripts/check_train_env.py`
  - current result on this machine: `ready_for_real_training = false`
  - reason: `torch 2.0.0` is below the current recommended server minimum

Current git target:

- branch: `main`
- remote: `origin`
- push target: `origin/main`

## Important caveats

`pilot_v1` is only a smoke dataset.

- it is derived from a toy seed, not the real BFCL clean slice
- its `dev` split is currently empty
- the checked-in LLaMA-Factory yaml files therefore use `*_test` as `eval_dataset`
- this is only for local smoke validation, not for paper experiments

Real paper evidence still requires:

- a BFCL-derived clean single-turn slice
- non-empty `train/dev/test`
- server-side LLaMA-Factory runs on a real `7B-8B+` backbone

## Handwritten trainer decision

Do not use the handwritten trainers for real baseline training.

Affected files:

- `scripts/train_direct.py`
- `scripts/train_latent.py`
- `scripts/train_reuse.py`
- `src/schema_reuse/train/direct.py`
- `src/schema_reuse/train/latent.py`
- `src/schema_reuse/train/reuse.py`

Current judgment:

- baseline training has already moved to `LLaMA-Factory`
- the handwritten trainer path is only `legacy / smoke-only / reference`
- it should not be extended for new baseline work

Why these files are not deleted yet:

- `reuse_main` is not fully re-homed yet
- some shared helpers under `src/schema_reuse/train/` still encode useful repo conventions
- immediate deletion would remove context for the next Codex session before the new runtime path is fully locked

Delete gate:

Delete the legacy handwritten trainers only after all three conditions are true:

1. the BFCL clean slice export path is working
2. at least one real LLaMA-Factory baseline run has succeeded on a training server
3. the implementation path for `reuse_main` is explicitly chosen
   - either a minimal LLaMA-Factory extension
   - or a separate method-side path that is not mistaken for the baseline runtime

## Current source of truth

Read these first:

- `STATUS.md`
- `HANDOFF.md`
- `2026-03-31-nips2026-function-calling-idea-draft-v2.md`
- `docs/superpowers/plans/2026-04-08-schema-reuse-pilot-v1-implementation-plan.md`
- `docs/superpowers/plans/2026-04-10-llamafactory-baseline-export-plan.md`
- `docs/status/deepresearch-status.md`
- `docs/status/pilot-v1-resource-estimate.md`

## Next recommended actions

1. Build a BFCL-derived clean single-turn slice with strict split hygiene.
2. Export that real slice into a new `data/llamafactory/<dataset_name>` directory.
3. Install the server training stack and LLaMA-Factory on the rented machine.
4. Run the three baseline families first:
   - `vanilla`
   - `schema_augmented`
   - `hammer_like`
5. Only after baseline runs are real, decide whether to delete the legacy handwritten trainers.
6. Only after baseline stability is confirmed, decide how `reuse_main` should be trained.
