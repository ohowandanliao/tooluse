# LLaMA-Factory Baselines

This document is a runtime / baseline document.
It is not the current paper's scientific claim document.

As of 2026-04-15, the active paper direction has shifted to
`measurement-first bottleneck attribution`:

- separate `decision`
- `interface-grounding`
- `search/calibration`

So the baselines described here should be read as engineering/runtime assets and
measurement instruments, not as the paper's current headline method.

The old handwritten baseline trainer path has been removed from this repo.
Baseline SFT and QLoRA runs should go through `llamafactory-cli` on exported
datasets.

## Workspace Hygiene

Treat the repo as releaseable source code.

- Keep the Python environment outside the repo.
- Keep editable third-party checkouts outside the repo.
- Keep training outputs outside the repo whenever possible.

Recommended runtime variables:

- `CONDA_BASE`
- `ENV_NAME`
- `ARTIFACT_ROOT`
- `XLAM_FC_ROOT`

## Export Baseline Datasets

The data flow has three layers:

- raw / official source data
- processed repo-internal JSONL under `data/processed/...`
- exported `LLaMA-Factory` datasets under `data/llamafactory/...`

The boundary is:

- repo-side build scripts create `data/processed/...`
- repo-side export scripts convert `data/processed/...` into `data/llamafactory/...`
- `llamafactory-cli train` consumes `data/llamafactory/...` for both training and its built-in prediction stage
- repo-side exact evaluation consumes `generated_predictions.jsonl` plus `data/processed/.../test.jsonl`

Current practical repo state:

- the checked-in xLAM baseline runs train directly from `data/llamafactory/xlam_fc_single_call/...`
- a fresh clone does not need the full processed split directory just to start training
- the extra file needed for repo-side exact evaluation is `data/processed/xlam_fc_single_call/test.jsonl`

```bash
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python scripts/export_llamafactory_baselines.py \
  --processed-dir data/processed/pilot_v1 \
  --output-dir data/llamafactory/pilot_v1
```

This writes:

- `data/llamafactory/pilot_v1/dataset_info.json`
- `pilot_v1_vanilla_{train,eval,test}.json`
- `pilot_v1_schema_augmented_{train,eval,test}.json`
- `pilot_v1_hammer_like_{train,eval,test}.json`

The exporter also reports `dataset_record_counts` and `empty_datasets`.
For the current toy `pilot_v1`, the `dev` split is empty, so the exported
`*_eval.json` files are empty by design.

## Run A Baseline

Replace `REPLACE_WITH_MODEL_NAME_OR_PATH` in the generic yaml files with the
actual backbone.

The checked-in `pilot_v1` yaml files intentionally use `*_test` as
`eval_dataset` because `pilot_v1/dev.jsonl` is empty. When switching to a real
BFCL-derived slice, move them back to the proper `*_eval` datasets.

Examples:

```bash
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" llamafactory-cli train configs/llamafactory/qwen_vanilla_sft_lora.yaml
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" llamafactory-cli train configs/llamafactory/qwen_schema_augmented_sft_lora.yaml
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" llamafactory-cli train configs/llamafactory/qwen_hammer_like_lora.yaml
```

These runs read exported datasets from `data/llamafactory/...`, not directly from `data/processed/...`.

## Current Scope

- `vanilla_sft`: `A-only direct SFT`; train on schema `T_A` only.
- `schema_augmented_sft`: `paired A+B direct SFT`; train on both `T_A` and
  `T_B`.
- `hammer_like`: `paired A+B direct SFT` plus irrelevant-tool injection in the
  tool list.

Naming note:

- `schema_augmented_sft` is a narrow baseline name in this repo
- it does not mean arbitrary schema augmentation, paraphrase generation,
  masking, or multi-stage reasoning
- it specifically means paired `T_A / y_A` and `T_B / y_B` supervision in one
  direct SFT pool

The current `hammer_like` path is still a data-level approximation. It does not
yet implement training-time name masking inside `LLaMA-Factory`, and it does
not yet match the full `Hammer` recipe with irrelevance-focused training data.

## Local 2080 Ti Bring-Up

On 2026-04-12, the repo was also verified on a local `RTX 2080 Ti 22GB` machine
with:

- hub workaround: `USE_MODELSCOPE_HUB=1`
- backbone: `Qwen/Qwen2.5-0.5B-Instruct`
- runtime: `4-bit QLoRA + fp16`

Machine-specific configs added for that path:

- `configs/llamafactory/local_qwen25_05b_vanilla_qlora.yaml`
- `configs/llamafactory/local_qwen25_05b_schema_augmented_qlora.yaml`
- `configs/llamafactory/local_qwen25_05b_hammer_like_qlora.yaml`
- `configs/llamafactory/local_qwen25_05b_vanilla_overfit_trainbook_qlora.yaml`

These machine-specific configs are expected to write outside the repo, for example:

- `$ARTIFACT_ROOT/runs/local_2080ti/...`

Example:

```bash
USE_MODELSCOPE_HUB=1 "$CONDA_BASE/bin/conda" run -n "$ENV_NAME" llamafactory-cli train \
  configs/llamafactory/local_qwen25_05b_vanilla_qlora.yaml
```

## Evaluate Exact Tool-Call Correctness

Do not rely on BLEU or ROUGE for function-calling evaluation.

Use the repo-side evaluator:

```bash
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python scripts/eval_llamafactory_predictions.py \
  --predictions "$ARTIFACT_ROOT/runs/local_2080ti/pilot_v1/qwen25_05b_vanilla_qlora/generated_predictions.jsonl" \
  --processed-jsonl data/processed/pilot_v1/test.jsonl \
  --mode vanilla
```

Important boundary:

- `generated_predictions.jsonl` comes from `LLaMA-Factory`
- `--processed-jsonl` is only for repo-side gold metadata / exact evaluation
- it is not the dataset consumed by `llamafactory-cli train`

The report includes:

- parsed prediction rate
- exact tool-call match
- tool-name match
- argument-key exact match
- argument-value exact match
- grouped exact-match breakdowns when processed metadata is provided
- by default, the report is written as `toolcall_eval.json` next to
  `generated_predictions.jsonl`

## Current Caveats

- `predict_with_generate` on the current `LLaMA-Factory` stack also needs
  `jieba`, `nltk`, and `rouge-chinese`.
- The 2026-04-12 local runs are engineering bring-up only.
- `pilot_v1` is too small and too toy-like to support paper claims.
