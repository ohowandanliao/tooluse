# tooluse

`tooluse` is a research codebase for NeurIPS 2026 function-calling experiments on
schema-reusable decision representations.

The current question is narrow: can a decision learned under tool schema `T_A` be
reused under an equivalent schema `T_B`? This repo is not trying to become a
general agent framework, and the active baseline runtime is `LLaMA-Factory`.

## Documentation Entry Points

- `RULES.md`: user-editable project rules and working principles
- `docs/PROJECT_RULES.md`: project principles, documentation rules, and artifact
  policy
- `STATUS.md`: current implementation/runtime status
- `HANDOFF.md`: cross-machine and cross-session handoff
- `results/README.md`: in-repo experiment evidence bundles
- `docs/new-machine-quickstart.md`: shortest path for bringing up a new machine and starting training
  including multi-machine experiment assignment and `pilot2000` extras
- `docs/environment-repro.md`: how to rebuild the validated environment on a new machine
- `docs/README.md`: document map by role

## Scope

- Study `cross-schema decision reuse` for function calling.
- Use `A->B` counterfactual decoding and `shuffle/null` controls as the main
  evidence path.
- Keep `RL` and execution-feedback distillation out of the current mainline.

## What Is In The Repo

- Paired-schema data construction for the current `pilot_v1` toy slice.
- Exporters that turn processed rows into `LLaMA-Factory` ShareGPT-with-tools
  datasets.
- Baseline configs for `vanilla`, `schema_augmented`, and `hammer_like`.
- Exact tool-call evaluation utilities for `generated_predictions.jsonl`.
- The old handwritten baseline trainer path has been removed from the codebase.

## Quickstart

Use a Python 3.11 environment outside the repo.

If you are restoring on a new machine without Codex, read
`docs/new-machine-quickstart.md` first. For the full recovery version, read
`docs/environment-repro.md`.

Shell variables used below:

```bash
export CONDA_BASE="${CONDA_BASE:-$(conda info --base)}"
export ENV_NAME="${ENV_NAME:-tooluse-llf}"
export ARTIFACT_ROOT="${ARTIFACT_ROOT:-../tooluse-artifacts}"
export XLAM_FC_ROOT="${XLAM_FC_ROOT:-$ARTIFACT_ROOT/external/xlam}"
```

Bootstrap entry:

```bash
bash scripts/bootstrap_train_env.sh --help
```

```bash
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python -m pytest -q
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python scripts/build_pilot_slice.py --config configs/pilot_v1/data.yaml
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python scripts/build_paired_dataset.py --config configs/pilot_v1/data.yaml
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python scripts/export_llamafactory_baselines.py
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python scripts/check_train_env.py
```

Build the current real-data baseline source from a local xLAM dump:

```bash
XLAM_FC_ROOT="$XLAM_FC_ROOT" \
  "$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python scripts/build_xlam_fc_single_call_slice.py \
  --config configs/xlam_fc_single_call/data.json

"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python scripts/build_paired_dataset.py \
  --config configs/xlam_fc_single_call/data.json

"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python scripts/export_llamafactory_baselines.py \
  --processed-dir data/processed/xlam_fc_single_call \
  --output-dir data/llamafactory/xlam_fc_single_call \
  --dataset-prefix xlam_fc_single_call
```

Meaning:

- `data/processed/xlam_fc_single_call`: repo-internal processed rows
- `data/llamafactory/xlam_fc_single_call`: actual `LLaMA-Factory` train/predict input

Current practical note:

- a fresh clone can start xLAM baseline training from `data/llamafactory/xlam_fc_single_call`
- repo-side exact evaluation still needs `data/processed/xlam_fc_single_call/test.jsonl`

Local 2080 Ti bring-up example:

```bash
USE_MODELSCOPE_HUB=1 "$CONDA_BASE/bin/conda" run -n "$ENV_NAME" llamafactory-cli train \
  configs/llamafactory/local_qwen25_05b_vanilla_qlora.yaml
```

Current xLAM pilot example:

```bash
USE_MODELSCOPE_HUB=1 "$CONDA_BASE/bin/conda" run -n "$ENV_NAME" llamafactory-cli train \
  configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_vanilla_qlora_pilot1000.yaml
```

Evaluate exact function-call correctness from a LLaMA-Factory prediction file:

```bash
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python scripts/eval_llamafactory_predictions.py \
  --predictions "$ARTIFACT_ROOT/runs/local_2080ti/pilot_v1/qwen25_05b_vanilla_qlora/generated_predictions.jsonl" \
  --processed-jsonl data/processed/pilot_v1/test.jsonl \
  --mode vanilla
```

Copy lightweight run evidence back into the repo:

```bash
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python scripts/summarize_run_results.py \
  --run-root "$ARTIFACT_ROOT/runs/local_2080ti/pilot_v1" \
  --output-dir results/local_2080ti/pilot_v1 \
  --machine local_2080ti \
  --experiment-group pilot_v1 \
  --dataset pilot_v1 \
  --include-generated-predictions
```

## Artifact Policy

Treat this repo as releaseable open-source code, not as a scratch directory.

- Keep conda environments outside the repo.
- Keep editable third-party checkouts outside the repo.
- Keep checkpoints and other heavy artifacts outside the repo.
- Keep lightweight experiment evidence in-repo under `results/`:
  commands, scalar metrics, exact-eval outputs, logs, and small prediction dumps
  when they remain lightweight.
- A recommended artifact-root convention is a repo-adjacent directory such as
  `../tooluse-artifacts`.

## Repository Map

- `STATUS.md`: current implementation/runtime status and project guardrails.
- `HANDOFF.md`: machine-to-machine handoff for a new Codex/GPT session.
- `RULES.md`: user-maintained rules entrypoint for this repo.
- `docs/PROJECT_RULES.md`: project principles and documentation conventions.
- `2026-03-31-nips2026-function-calling-idea-draft-v2.md`: current scientific
  draft.
- `configs/`: data and training configs.
- `scripts/`: data build, export, evaluation, and training entrypoints.
- `results/`: committed experiment evidence bundles without weights.
- `src/schema_reuse/`: library code for data, export, models, and evaluation.
- `tests/`: regression tests for export, training utilities, and evaluation.
- `docs/README.md`: document index and archive policy.

## Current Limitations

- `pilot_v1` is still only a smoke dataset.
- The current `pilot_v1/dev.jsonl` split is empty.
- The 2026-04-12 local QLoRA runs are engineering bring-up evidence, not paper
  evidence.
- The training path for `reuse_main` is still unresolved and should not be
  confused with the baseline runtime.
