# Local 2080 Ti QLoRA Bring-Up

Date: 2026-04-12

This note records the first real LLaMA-Factory bring-up on the local `RTX 2080 Ti 22GB` machine.

## Scope

This was an engineering bring-up, not a paper experiment.

Goals:

- verify that `pilot_v1 -> export -> LLaMA-Factory -> predict` works end-to-end
- avoid the handwritten trainer path
- check whether a modest single GPU can run the baseline stack

Non-goals:

- scientific claims from `pilot_v1`
- BFCL evidence
- `reuse_main` evaluation

## Environment

Dedicated env:

- `tooluse-llf`

Artifact root:

- repo 外的 `ARTIFACT_ROOT`

Editable LLaMA-Factory checkout:

- `$ARTIFACT_ROOT/external/LLaMA-Factory`

Known-good versions:

- Python `3.11.15`
- PyTorch `2.6.0+cu124`
- Transformers `5.2.0`
- Datasets `4.0.0`
- Accelerate `1.11.0`
- PEFT `0.18.1`
- TRL `0.24.0`
- Bitsandbytes `0.49.2`
- LLaMA-Factory `0.9.5.dev0`

Model download workaround that worked:

- `USE_MODELSCOPE_HUB=1`

Backbone used for bring-up:

- `Qwen/Qwen2.5-0.5B-Instruct`

## Commands that were run

Data pipeline:

```bash
python3 scripts/build_pilot_slice.py --config configs/pilot_v1/data.yaml
python3 scripts/build_paired_dataset.py --config configs/pilot_v1/data.yaml
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python scripts/export_llamafactory_baselines.py
```

Local baseline runs:

```bash
USE_MODELSCOPE_HUB=1 "$CONDA_BASE/bin/conda" run -n "$ENV_NAME" llamafactory-cli train \
  configs/llamafactory/local_qwen25_05b_vanilla_qlora.yaml

USE_MODELSCOPE_HUB=1 "$CONDA_BASE/bin/conda" run -n "$ENV_NAME" llamafactory-cli train \
  configs/llamafactory/local_qwen25_05b_schema_augmented_qlora.yaml

USE_MODELSCOPE_HUB=1 "$CONDA_BASE/bin/conda" run -n "$ENV_NAME" llamafactory-cli train \
  configs/llamafactory/local_qwen25_05b_hammer_like_qlora.yaml
```

Sanity overfit:

```bash
USE_MODELSCOPE_HUB=1 "$CONDA_BASE/bin/conda" run -n "$ENV_NAME" llamafactory-cli train \
  configs/llamafactory/local_qwen25_05b_vanilla_overfit_trainbook_qlora.yaml
```

## Results

Held-out toy runs:

- `vanilla`
  - output archive: `$ARTIFACT_ROOT/runs/local_2080ti/pilot_v1/qwen25_05b_vanilla_qlora`
  - exact-eval report: `toolcall_eval.json`
  - train loss: `0.0014169`
  - exact tool-call match: `0/1`
  - name match rate: `1.0`
  - argument-key match rate: `1.0`
- `schema_augmented`
  - output archive: `$ARTIFACT_ROOT/runs/local_2080ti/pilot_v1/qwen25_05b_schema_augmented_qlora`
  - exact-eval report: `toolcall_eval.json`
  - train loss: `0.0094497`
  - exact tool-call match: `0/2`
  - name match rate: `1.0`
  - argument-key match rate: `1.0`
- `hammer_like`
  - output archive: `$ARTIFACT_ROOT/runs/local_2080ti/pilot_v1/qwen25_05b_hammer_like_qlora`
  - exact-eval report: `toolcall_eval.json`
  - train loss: `0.0044566`
  - exact tool-call match: `0/2`
  - name match rate: `1.0`
  - argument-key match rate: `1.0`

Sanity overfit run:

- output archive: `$ARTIFACT_ROOT/runs/local_2080ti/pilot_v1/qwen25_05b_vanilla_overfit_trainbook_qlora`
- exact-eval report: `toolcall_eval.json`
- exact tool-call match: `1/1`
- post-migration smoke rerun: success

## Qualitative error pattern

The held-out toy failures are consistent:

- `Book me a train from Beijing to Hangzhou` was decoded as:
  - `arrival_city = Beijing`
  - `departure_city = Hangzhou`
- under the aliased schema variant, the model also translated values:
  - `Beijing -> 北京`
  - `Hangzhou -> 杭州`

Interpretation:

- the model understands the correct tool identity and the correct argument slots
- it fails on role grounding and value copying under this tiny held-out setup
- the overfit sanity run shows the runtime path can produce exact calls when the target semantics are seen during training

## What this means

What this run established:

- LLaMA-Factory is the correct baseline runtime path for this repo
- the local machine can execute real QLoRA baseline training
- ModelScope is a workable fallback when Hugging Face download times out
- the exported ShareGPT-with-tools format is compatible with the `qwen` template

What this run did not establish:

- any scientific evidence for `cross-schema decision reuse`
- any meaningful comparison between `vanilla`, `schema_augmented`, and `hammer_like`
- anything publishable from `pilot_v1`

## Immediate implication for the project

The bottleneck is no longer baseline runtime bring-up.

The bottleneck is now:

- building a real BFCL-derived clean slice
- evaluating exact tool-call correctness instead of text overlap
- moving from toy semantics to a real held-out schema-transfer setting
