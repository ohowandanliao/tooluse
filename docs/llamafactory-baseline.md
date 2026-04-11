# LLaMA-Factory Baseline Export

This repo does not train the baseline models with a custom trainer anymore.
Instead, baseline SFT runs should use `llamafactory-cli` on exported datasets.

## Export Baseline Datasets

```bash
python3 scripts/export_llamafactory_baselines.py \
  --processed-dir data/processed/pilot_v1 \
  --output-dir data/llamafactory/pilot_v1
```

This writes:

- `data/llamafactory/pilot_v1/dataset_info.json`
- `pilot_v1_vanilla_{train,eval,test}.json`
- `pilot_v1_schema_augmented_{train,eval,test}.json`
- `pilot_v1_hammer_like_{train,eval,test}.json`

The exporter also reports `dataset_record_counts` and `empty_datasets`.
For the current toy `pilot_v1`, the `dev` split is empty, so the exported `*_eval.json` files are empty by design.

## Run A Baseline

Replace `REPLACE_WITH_MODEL_NAME_OR_PATH` in the yaml with the actual backbone.
The checked-in yaml files are smoke configs for `pilot_v1`, so they intentionally use `*_test` as `eval_dataset`.
When switching to a real BFCL-derived slice, change them back to the proper `*_eval` datasets.

Examples:

```bash
llamafactory-cli train configs/llamafactory/qwen_vanilla_sft_lora.yaml
llamafactory-cli train configs/llamafactory/qwen_schema_augmented_sft_lora.yaml
llamafactory-cli train configs/llamafactory/qwen_hammer_like_lora.yaml
```

## Current Scope

- `vanilla_sft`: schema `T_A` only
- `schema_augmented_sft`: both `T_A` and `T_B`
- `hammer_like`: `schema_augmented_sft` plus irrelevant-tool injection in the tool list

The current `hammer_like` export is a data-level approximation.
It does not yet implement training-time name masking inside LLaMA-Factory.
