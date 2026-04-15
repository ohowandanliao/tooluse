# local_2080ti / pilot_v1 commands

默认都在仓库根目录执行，环境为：

- `tooluse-llf`

## 训练命令

```bash
USE_MODELSCOPE_HUB=1 "$CONDA_BASE/bin/conda" run -n "$ENV_NAME" llamafactory-cli train \
  configs/llamafactory/local_qwen25_05b_vanilla_qlora.yaml
```

```bash
USE_MODELSCOPE_HUB=1 "$CONDA_BASE/bin/conda" run -n "$ENV_NAME" llamafactory-cli train \
  configs/llamafactory/local_qwen25_05b_schema_augmented_qlora.yaml
```

```bash
USE_MODELSCOPE_HUB=1 "$CONDA_BASE/bin/conda" run -n "$ENV_NAME" llamafactory-cli train \
  configs/llamafactory/local_qwen25_05b_hammer_like_qlora.yaml
```

```bash
USE_MODELSCOPE_HUB=1 "$CONDA_BASE/bin/conda" run -n "$ENV_NAME" llamafactory-cli train \
  configs/llamafactory/local_qwen25_05b_vanilla_overfit_trainbook_qlora.yaml
```

## 精确评测命令

```bash
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python scripts/eval_llamafactory_predictions.py \
  --predictions "$ARTIFACT_ROOT/runs/local_2080ti/pilot_v1/qwen25_05b_vanilla_qlora/generated_predictions.jsonl" \
  --processed-jsonl data/processed/pilot_v1/test.jsonl \
  --mode vanilla
```

```bash
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python scripts/eval_llamafactory_predictions.py \
  --predictions "$ARTIFACT_ROOT/runs/local_2080ti/pilot_v1/qwen25_05b_schema_augmented_qlora/generated_predictions.jsonl" \
  --processed-jsonl data/processed/pilot_v1/test.jsonl \
  --mode schema_augmented
```

```bash
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python scripts/eval_llamafactory_predictions.py \
  --predictions "$ARTIFACT_ROOT/runs/local_2080ti/pilot_v1/qwen25_05b_hammer_like_qlora/generated_predictions.jsonl" \
  --processed-jsonl data/processed/pilot_v1/test.jsonl \
  --mode hammer_like
```

```bash
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python scripts/eval_llamafactory_predictions.py \
  --predictions "$ARTIFACT_ROOT/runs/local_2080ti/pilot_v1/qwen25_05b_vanilla_overfit_trainbook_qlora/generated_predictions.jsonl" \
  --processed-jsonl data/processed/pilot_v1/test.jsonl \
  --mode vanilla
```

## 刷新仓库内证据包

```bash
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python scripts/summarize_run_results.py \
  --run-root "$ARTIFACT_ROOT/runs/local_2080ti/pilot_v1" \
  --output-dir results/local_2080ti/pilot_v1 \
  --machine local_2080ti \
  --experiment-group pilot_v1 \
  --dataset pilot_v1 \
  --include-generated-predictions
```
