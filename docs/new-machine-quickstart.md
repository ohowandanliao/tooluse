# 新机器快速开始

这份文档只保留最短路径。

适用场景：

- 你拿到一台新机器；
- 不开 `Codex`；
- 想尽快把环境装起来并开始跑 baseline。

默认约定：

- 仓库路径：`/root/autodl-fs/tooluse`
- 重产物路径：`/root/autodl-fs/tooluse-artifacts`
- conda 根目录：`/root/miniconda3`
- 环境名：`tooluse-llf`

## 1. 拉代码

```bash
git clone <your-private-repo-url> /root/autodl-fs/tooluse
cd /root/autodl-fs/tooluse
```

如果你不是从 `git clone` 开始，而是直接把整个 `tooluse/` 文件夹拷到了新机器，也可以直接进入仓库目录。

## 2. 装环境

如果新机器已经有 `/root/miniconda3`，直接跑：

```bash
bash scripts/bootstrap_train_env.sh \
  --torch-install-cmd "pip install torch torchvision torchaudio"
```

如果你已经提前装好了可用的 `torch`，可以省掉 `--torch-install-cmd`：

```bash
bash scripts/bootstrap_train_env.sh
```

默认已经用了清华源。

## 3. 验证环境

```bash
/root/miniconda3/bin/conda run -n tooluse-llf python -m pytest -q
/root/miniconda3/bin/conda run -n tooluse-llf python scripts/check_train_env.py
```

预期：

- `pytest` 通过；
- `ready_for_real_training = true`

## 4. 准备数据

当前真实 baseline 主线用的是 `xLAM function-calling-60k`。

先把原始文件放到：

```bash
/root/autodl-fs/tooluse-artifacts/external/xlam/xlam_function_calling_60k.json
```

然后构建：

```bash
mkdir -p /root/autodl-fs/tooluse-artifacts/external/xlam

XLAM_FC_ROOT=/root/autodl-fs/tooluse-artifacts/external/xlam \
  /root/miniconda3/bin/conda run -n tooluse-llf python \
  scripts/build_xlam_fc_single_call_slice.py \
  --config configs/xlam_fc_single_call/data.json

/root/miniconda3/bin/conda run -n tooluse-llf python \
  scripts/build_paired_dataset.py \
  --config configs/xlam_fc_single_call/data.json

/root/miniconda3/bin/conda run -n tooluse-llf python \
  scripts/export_llamafactory_baselines.py \
  --processed-dir data/processed/xlam_fc_single_call \
  --output-dir data/llamafactory/xlam_fc_single_call \
  --dataset-prefix xlam_fc_single_call
```

如果你已经把旧机器上的下面两个目录直接拷到了新机器：

- `data/processed/xlam_fc_single_call/`
- `data/llamafactory/xlam_fc_single_call/`

那这一步可以跳过。

## 5. 开跑 baseline

这里的推荐策略不是“一台机器把三个都跑完”，而是：

- 每台机器只挑一个 baseline 配方；
- 用多台机器分担 `vanilla / schema_augmented / hammer_like`；
- 这样比在一台机器上串行排队更符合当前扩机器的目的。

推荐分工：

- 老机器继续跑当前已经在跑的那个 baseline；
- 新机器 A 跑 `schema_augmented`；
- 新机器 B 跑 `hammer_like`。

如果你现在只有一台新机器，那这台新机器只跑一个你最想先补齐的 baseline，不要默认把三个都排进去。

先准备环境变量：

```bash
export HF_HOME=/root/autodl-fs/tooluse-artifacts/cache/huggingface
export MODELSCOPE_CACHE=/root/autodl-fs/tooluse-artifacts/cache/modelscope
export PIP_CACHE_DIR=/root/autodl-fs/tooluse-artifacts/cache/pip
export USE_MODELSCOPE_HUB=1
```

### 5.1 `vanilla`

如果这台机器就是专门拿来补 `vanilla` 的，再跑这条：

```bash
/root/miniconda3/bin/conda run -n tooluse-llf llamafactory-cli train \
  configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_vanilla_qlora_pilot1000.yaml
```

### 5.2 `schema_augmented`

如果这台机器分配给 `schema_augmented`，跑这条：

```bash
/root/miniconda3/bin/conda run -n tooluse-llf llamafactory-cli train \
  configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_schema_augmented_qlora_pilot1000.yaml
```

### 5.3 `hammer_like`

如果这台机器分配给 `hammer_like`，跑这条：

```bash
/root/miniconda3/bin/conda run -n tooluse-llf llamafactory-cli train \
  configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_hammer_like_qlora_pilot1000.yaml
```

## 6. 看日志

三个 run 目录分别是：

- `vanilla`
  - `/root/autodl-fs/tooluse-artifacts/runs/local_2080ti/xlam_fc_single_call/qwen25_05b_vanilla_qlora_pilot1000`
- `schema_augmented`
  - `/root/autodl-fs/tooluse-artifacts/runs/local_2080ti/xlam_fc_single_call/qwen25_05b_schema_augmented_qlora_pilot1000`
- `hammer_like`
  - `/root/autodl-fs/tooluse-artifacts/runs/local_2080ti/xlam_fc_single_call/qwen25_05b_hammer_like_qlora_pilot1000`

比如看日志：

```bash
tail -f /root/autodl-fs/tooluse-artifacts/runs/local_2080ti/xlam_fc_single_call/qwen25_05b_vanilla_qlora_pilot1000/launch.log
tail -f /root/autodl-fs/tooluse-artifacts/runs/local_2080ti/xlam_fc_single_call/qwen25_05b_schema_augmented_qlora_pilot1000/launch.log
tail -f /root/autodl-fs/tooluse-artifacts/runs/local_2080ti/xlam_fc_single_call/qwen25_05b_hammer_like_qlora_pilot1000/launch.log
```

## 7. 跑评测

预测跑完后，只评测这台机器实际跑的那个模式。

### 7.1 评测 `vanilla`

```bash
/root/miniconda3/bin/conda run -n tooluse-llf python \
  scripts/eval_llamafactory_predictions.py \
  --predictions /root/autodl-fs/tooluse-artifacts/runs/local_2080ti/xlam_fc_single_call/qwen25_05b_vanilla_qlora_pilot1000/generated_predictions.jsonl \
  --processed-jsonl data/processed/xlam_fc_single_call/test.jsonl \
  --mode vanilla
```

### 7.2 评测 `schema_augmented`

```bash
/root/miniconda3/bin/conda run -n tooluse-llf python \
  scripts/eval_llamafactory_predictions.py \
  --predictions /root/autodl-fs/tooluse-artifacts/runs/local_2080ti/xlam_fc_single_call/qwen25_05b_schema_augmented_qlora_pilot1000/generated_predictions.jsonl \
  --processed-jsonl data/processed/xlam_fc_single_call/test.jsonl \
  --mode schema_augmented
```

### 7.3 评测 `hammer_like`

```bash
/root/miniconda3/bin/conda run -n tooluse-llf python \
  scripts/eval_llamafactory_predictions.py \
  --predictions /root/autodl-fs/tooluse-artifacts/runs/local_2080ti/xlam_fc_single_call/qwen25_05b_hammer_like_qlora_pilot1000/generated_predictions.jsonl \
  --processed-jsonl data/processed/xlam_fc_single_call/test.jsonl \
  --mode hammer_like
```

## 8. 把轻量结果同步回仓库

如果这台机器只跑了一个 baseline，这条命令也只会同步那个 run。

```bash
/root/miniconda3/bin/conda run -n tooluse-llf python \
  scripts/summarize_run_results.py \
  --run-root /root/autodl-fs/tooluse-artifacts/runs/local_2080ti/xlam_fc_single_call \
  --output-dir results/local_2080ti/xlam_fc_single_call \
  --machine local_2080ti \
  --experiment-group xlam_fc_single_call \
  --dataset xlam_fc_single_call \
  --include-generated-predictions
```

## 最短理解

新机器最短流程其实就四步：

1. `git clone`
2. `bash scripts/bootstrap_train_env.sh`
3. 构建 `xLAM` 数据
4. 这台机器只选一个 baseline 开跑
