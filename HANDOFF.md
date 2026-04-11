# HANDOFF

This file is for a new Codex or GPT session taking over the repo on another machine.

Repository target at the time of writing:

- branch: `main`
- remote: `origin`
- default push target: `origin/main`

## Read order

Read these files in this order:

1. `STATUS.md`
2. `2026-03-31-nips2026-function-calling-idea-draft-v2.md`
3. `docs/status/deepresearch-status.md`
4. `docs/superpowers/plans/2026-04-08-schema-reuse-pilot-v1-implementation-plan.md`
5. `docs/superpowers/plans/2026-04-10-llamafactory-baseline-export-plan.md`
6. `docs/llamafactory-baseline.md`

## What the project is actually trying to prove

The current paper is not about:

- general agent frameworks
- RL as a headline method
- feedback posterior distillation as the main contribution

It is about:

- `schema-reusable decision representation`
- proving reuse through `A->B` counterfactual decoding
- showing `A->B > shuffle/null`
- checking whether the gain survives held-out schema transforms

## Source-of-truth implementation paths

The active runtime path for baselines is:

- export processed paired-schema rows into LLaMA-Factory datasets
- run baseline SFT with `llamafactory-cli`

Main files for that path:

- `src/schema_reuse/export/llamafactory.py`
- `scripts/export_llamafactory_baselines.py`
- `configs/llamafactory/qwen_vanilla_sft_lora.yaml`
- `configs/llamafactory/qwen_schema_augmented_sft_lora.yaml`
- `configs/llamafactory/qwen_hammer_like_lora.yaml`
- `docs/llamafactory-baseline.md`
- `tests/export/test_llamafactory.py`

Current processed toy data:

- `data/processed/pilot_v1/train.jsonl`
- `data/processed/pilot_v1/dev.jsonl`
- `data/processed/pilot_v1/test.jsonl`

Current exported toy baseline data:

- `data/llamafactory/pilot_v1/`

## Legacy path that should not be treated as the runtime

These files are legacy smoke/reference only:

- `scripts/train_direct.py`
- `scripts/train_latent.py`
- `scripts/train_reuse.py`
- `src/schema_reuse/train/direct.py`
- `src/schema_reuse/train/latent.py`
- `src/schema_reuse/train/reuse.py`

Interpret them as:

- old scaffolding
- useful for understanding naming and metrics conventions
- not the correct baseline training path anymore

Do not build new baseline work on top of them.

## Verified local commands

Run from repo root.

### Tests

```bash
python3 -m pytest -q
```

Expected at the time of writing:

- `18 passed`

### Baseline export

```bash
python3 scripts/export_llamafactory_baselines.py
```

Expected at the time of writing:

- exports files into `data/llamafactory/pilot_v1`
- reports empty datasets for:
  - `pilot_v1_vanilla_eval`
  - `pilot_v1_schema_augmented_eval`
  - `pilot_v1_hammer_like_eval`

This is expected because `pilot_v1/dev.jsonl` is empty.

### Training environment probe

```bash
python3 scripts/check_train_env.py
```

Expected on the current local machine:

- `ready_for_real_training = false`
- reason: `torch 2.0.0` is too old for the intended server stack

## What should happen next

The next owner should do this, in order:

1. Keep the scientific scope narrow.
   - no RL mainline
   - no feedback-mainline resurrection
   - no framework paper drift
2. Replace the toy `pilot_v1` evidence path with a BFCL-derived clean slice.
3. Export that real slice into LLaMA-Factory format.
4. Run real baseline training on a proper server.
5. Evaluate the baseline results before deciding anything large about `reuse_main`.
6. Only then revisit deletion of the legacy handwritten trainer files.

## What not to do

Do not:

- claim paper evidence from `pilot_v1`
- extend the handwritten baseline trainers
- delete the legacy trainer files before the delete gate in `STATUS.md`
- add RL just because a later phase might use it
- broaden the paper back into a tool-use framework story

## If you need a server

Current environment guidance:

- see `docs/status/pilot-v1-resource-estimate.md`
- see `requirements/train-server.txt`

The practical target remains:

- `1x A100 80GB` or `1x H100 80GB`, preferred
- a strong `48GB` GPU is workable but slower and tighter

## If you need to continue cleanup

Safe cleanup now:

- improve docs
- archive obsolete PDFs if already summarized
- tighten the BFCL clean-slice pipeline
- add real-data exporter coverage

Cleanup to defer:

- deleting `src/schema_reuse/train/*.py`
- deleting `scripts/train_*.py`
- deleting train-config tests that still document legacy assumptions
