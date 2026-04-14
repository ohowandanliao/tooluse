# local_2080ti / pilot_v1 commands

默认都在仓库根目录执行，环境为：

- `/root/miniconda3/envs/tooluse-llf`

## 训练命令

```bash
USE_MODELSCOPE_HUB=1 /root/miniconda3/envs/tooluse-llf/bin/llamafactory-cli train \
  configs/llamafactory/local_qwen25_05b_vanilla_qlora.yaml
```

```bash
USE_MODELSCOPE_HUB=1 /root/miniconda3/envs/tooluse-llf/bin/llamafactory-cli train \
  configs/llamafactory/local_qwen25_05b_schema_augmented_qlora.yaml
```

```bash
USE_MODELSCOPE_HUB=1 /root/miniconda3/envs/tooluse-llf/bin/llamafactory-cli train \
  configs/llamafactory/local_qwen25_05b_hammer_like_qlora.yaml
```

```bash
USE_MODELSCOPE_HUB=1 /root/miniconda3/envs/tooluse-llf/bin/llamafactory-cli train \
  configs/llamafactory/local_qwen25_05b_vanilla_overfit_trainbook_qlora.yaml
```

## 精确评测命令

```bash
/root/miniconda3/envs/tooluse-llf/bin/python scripts/eval_llamafactory_predictions.py \
  --predictions /root/autodl-fs/tooluse-artifacts/runs/local_2080ti/pilot_v1/qwen25_05b_vanilla_qlora/generated_predictions.jsonl \
  --processed-jsonl data/processed/pilot_v1/test.jsonl \
  --mode vanilla
```

```bash
/root/miniconda3/envs/tooluse-llf/bin/python scripts/eval_llamafactory_predictions.py \
  --predictions /root/autodl-fs/tooluse-artifacts/runs/local_2080ti/pilot_v1/qwen25_05b_schema_augmented_qlora/generated_predictions.jsonl \
  --processed-jsonl data/processed/pilot_v1/test.jsonl \
  --mode schema_augmented
```

```bash
/root/miniconda3/envs/tooluse-llf/bin/python scripts/eval_llamafactory_predictions.py \
  --predictions /root/autodl-fs/tooluse-artifacts/runs/local_2080ti/pilot_v1/qwen25_05b_hammer_like_qlora/generated_predictions.jsonl \
  --processed-jsonl data/processed/pilot_v1/test.jsonl \
  --mode hammer_like
```

```bash
/root/miniconda3/envs/tooluse-llf/bin/python scripts/eval_llamafactory_predictions.py \
  --predictions /root/autodl-fs/tooluse-artifacts/runs/local_2080ti/pilot_v1/qwen25_05b_vanilla_overfit_trainbook_qlora/generated_predictions.jsonl \
  --processed-jsonl data/processed/pilot_v1/test.jsonl \
  --mode vanilla
```

## 刷新仓库内证据包

```bash
/root/miniconda3/envs/tooluse-llf/bin/python scripts/summarize_run_results.py \
  --run-root /root/autodl-fs/tooluse-artifacts/runs/local_2080ti/pilot_v1 \
  --output-dir results/local_2080ti/pilot_v1 \
  --machine local_2080ti \
  --experiment-group pilot_v1 \
  --dataset pilot_v1 \
  --include-generated-predictions
```
