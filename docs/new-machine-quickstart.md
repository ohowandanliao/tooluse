# 新机器快速开始

这份文档面向“新机器尽快起一个 baseline”。

先强调一句：

- 这份文档服务的是 baseline runtime / bring-up
- 不是当前论文主线的最终 scientific framing 文档
- 截至 `2026-04-15`，当前论文主线已经切到
  `measurement-first bottleneck attribution`
- 所以这里的训练任务应理解为：
  - baseline bring-up
  - schema sensitivity instrument
  - direct baseline reference
  而不是默认的最终论文主结果

目标只有三个：

- 尽快把环境装起来；
- 尽快开跑一个不和别的机器重复的 baseline；
- 训练完后，能把结果准确回传给当前主仓库。

这份文档现在已经把“环境恢复”和“多机实验分配”合到一起了。

如果有些步骤你已经做过，可以直接跳：

- 环境已经装好：
  - 直接跳到第 4 节
- 数据已经齐：
  - 直接跳到第 6 节
- 你只想知道“这台机器该跑哪个实验”：
  - 直接跳到第 12 节

## 0. 先约定变量

下面这一步先只约定“和 repo 无关”的变量。

```bash
export CONDA_BASE="${CONDA_BASE:-$(conda info --base)}"
export ENV_NAME="${ENV_NAME:-tooluse-llf}"
export ARTIFACT_ROOT="${ARTIFACT_ROOT:-../tooluse-artifacts}"
export MACHINE_LABEL="${MACHINE_LABEL:-$(hostname -s)}"
export EXP_GROUP="xlam_fc_single_call"

mkdir -p \
  "$ARTIFACT_ROOT/cache/huggingface" \
  "$ARTIFACT_ROOT/cache/modelscope" \
  "$ARTIFACT_ROOT/cache/pip" \
  "$ARTIFACT_ROOT/runs/$MACHINE_LABEL/$EXP_GROUP"
```

如果当前 shell 里没有 `conda`，就手动指定：

```bash
export CONDA_BASE=/path/to/your/miniconda-or-anaconda
```

## 1. 拉代码

```bash
git clone --depth 1 <your-private-repo-url> tooluse
cd tooluse
export REPO_ROOT="$(pwd)"
```

如果你不是从 `git clone` 开始，而是直接把整个仓库目录拷到了新机器，也可以直接进入 repo 根目录。

## 2. 装环境

推荐直接跑 bootstrap 脚本。

如果这台机器还没有可用的 `torch`：

```bash
bash scripts/bootstrap_train_env.sh \
  --conda-root "$CONDA_BASE" \
  --env-name "$ENV_NAME" \
  --artifact-root "$ARTIFACT_ROOT" \
  --torch-install-cmd "pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0"
```

如果机器上已经提前装好了目标 `torch`：

```bash
bash scripts/bootstrap_train_env.sh \
  --conda-root "$CONDA_BASE" \
  --env-name "$ENV_NAME" \
  --artifact-root "$ARTIFACT_ROOT"
```

如果 repo 依赖安装慢，可以切到国内源，例如中科大：

```bash
bash scripts/bootstrap_train_env.sh \
  --conda-root "$CONDA_BASE" \
  --env-name "$ENV_NAME" \
  --artifact-root "$ARTIFACT_ROOT" \
  --pip-index-url https://pypi.mirrors.ustc.edu.cn/simple
```

## 3. 验证环境

```bash
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python -m pytest -q
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python scripts/check_train_env.py
```

预期：

- `pytest` 通过；
- `ready_for_real_training = true`

## 4. 先把数据层分清楚

这个项目里有三层数据：

- 原始数据：
  - 例如 `xlam_function_calling_60k.json`
- repo 内部中间层：
  - `data/processed/xlam_fc_single_call/`
- `LLaMA-Factory` 训练/预测输入层：
  - `data/llamafactory/xlam_fc_single_call/`

准确关系是：

- `build_*` 脚本先把原始数据整理成 `data/processed/...`
- `export_llamafactory_baselines.py` 再把 `data/processed/...` 导出成 `data/llamafactory/...`
- `llamafactory-cli train` 的训练和它内部的 prediction，**都读** `data/llamafactory/...`
- repo 自己的 `scripts/eval_llamafactory_predictions.py` 做 exact evaluator 时，才会再读 `data/processed/.../test.jsonl`

也就是说：

- 训练用的是 `data/llamafactory/...`
- prediction 用的也是 `data/llamafactory/...`
- `data/processed/...` 主要用于导出和离线精确评测

当前仓库的实际状态再说白一点：

- fresh clone 之后，训练可以直接开始，因为 repo 里已经带了 `data/llamafactory/xlam_fc_single_call/`
- fresh clone 之后，repo 自己的 exact evaluator 还不能直接跑，除非你另外拿到 `data/processed/xlam_fc_single_call/test.jsonl`
- 所以当前不是“训练和评测都依赖整套 processed 数据”，而是：
  - 训练/内置 prediction：依赖 `data/llamafactory/...`
  - repo-side exact evaluator：只额外依赖 `data/processed/.../test.jsonl`

## 5. 数据怎么准备

### 5.1 最快路径

如果下面这个文件存在：

```bash
test -f data/llamafactory/xlam_fc_single_call/dataset_info.json
```

那就可以直接开始训练，不必先重建原始 xLAM。

这也是新机器最推荐的路径。

### 5.2 什么时候才需要重建

只有这两种情况才需要重建：

- repo 里没有 `data/llamafactory/xlam_fc_single_call/`
- 你后面还要跑 exact evaluator，但本地没有 `data/processed/xlam_fc_single_call/test.jsonl`

如果你只是想先把训练跑起来，当前 repo 状态下并不要求先重建 `processed`。

如果要从原始 xLAM 重建，先准备：

```bash
export XLAM_FC_ROOT="${XLAM_FC_ROOT:-$ARTIFACT_ROOT/external/xlam}"
mkdir -p "$XLAM_FC_ROOT"
ls "$XLAM_FC_ROOT/xlam_function_calling_60k.json"
```

然后执行：

```bash
XLAM_FC_ROOT="$XLAM_FC_ROOT" \
  "$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python \
  scripts/build_xlam_fc_single_call_slice.py \
  --config configs/xlam_fc_single_call/data.json

"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python \
  scripts/build_paired_dataset.py \
  --config configs/xlam_fc_single_call/data.json

"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python \
  scripts/export_llamafactory_baselines.py \
  --processed-dir data/processed/xlam_fc_single_call \
  --output-dir data/llamafactory/xlam_fc_single_call \
  --dataset-prefix xlam_fc_single_call
```

## 6. 这台机器跑哪个 baseline

默认策略不是“一台机器把三个 baseline 都跑完”，而是：

- 每台机器只跑一个 baseline；
- 多台机器分担 `vanilla / schema_augmented / hammer_like`；
- 避免重复。

当前推荐分工：

- 老机器：`hammer_like`
- 新机器：`schema_augmented`

如果你要跑别的模式，也可以改，但一定要先确认不要和别的机器撞车。

这里的 mode 名字要按仓库内的窄口径理解：

- `vanilla`：
  - `A-only direct SFT`
- `schema_augmented`：
  - `paired A+B direct SFT`
  - 不是泛指各种 schema augmentation recipe
- `hammer_like`：
  - `paired A+B direct SFT` + irrelevant-tool injection
  - 目前只是 repo 内的近似版，不等于完整 `Hammer`

先设置本机这次 run 的变量。

如果你这台机器跑 `schema_augmented`：

```bash
export MODE="schema_augmented"
export CONFIG="configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_schema_augmented_qlora_pilot1000.yaml"
export RUN_NAME="qwen25_05b_schema_augmented_qlora_pilot1000"
```

如果你这台机器跑 `hammer_like`：

```bash
export MODE="hammer_like"
export CONFIG="configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_hammer_like_qlora_pilot1000.yaml"
export RUN_NAME="qwen25_05b_hammer_like_qlora_pilot1000"
```

如果你这台机器跑 `vanilla`：

```bash
export MODE="vanilla"
export CONFIG="configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_vanilla_qlora_pilot1000.yaml"
export RUN_NAME="qwen25_05b_vanilla_qlora_pilot1000"
```

统一 run 目录：

```bash
export RUN_ROOT="$ARTIFACT_ROOT/runs/$MACHINE_LABEL/$EXP_GROUP"
export RUN_DIR="$RUN_ROOT/$RUN_NAME"
mkdir -p "$RUN_DIR"
```

## 7. 开跑训练

先准备缓存变量：

```bash
export HF_HOME="$ARTIFACT_ROOT/cache/huggingface"
export MODELSCOPE_CACHE="$ARTIFACT_ROOT/cache/modelscope"
export PIP_CACHE_DIR="$ARTIFACT_ROOT/cache/pip"
export USE_MODELSCOPE_HUB=1
```

前台直接跑：

```bash
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" bash -lc "
  cd '$REPO_ROOT' &&
  llamafactory-cli train '$CONFIG' output_dir='$RUN_DIR'
"
```

如果要后台挂着跑：

```bash
nohup "$CONDA_BASE/bin/conda" run -n "$ENV_NAME" bash -lc "
  cd '$REPO_ROOT' &&
  llamafactory-cli train '$CONFIG' output_dir='$RUN_DIR'
" > "$RUN_DIR/launch.log" 2>&1 &
```

注意：

- 这里的 `llamafactory-cli train` 同时包含训练和它内部的 prediction
- 训练和 prediction 都读 `data/llamafactory/xlam_fc_single_call/`
- 不是直接读 `data/processed/xlam_fc_single_call/`

## 8. 看日志

```bash
tail -f "$RUN_DIR/launch.log"
tail -f "$RUN_DIR/trainer_log.jsonl"
```

经验上：

- `launch.log` 更适合看启动、下载、报错、prediction 进度
- `trainer_log.jsonl` 更适合看 step、loss、训练曲线

## 9. 跑 exact evaluator

这一节只有在你本地已经有：

```bash
test -f data/processed/xlam_fc_single_call/test.jsonl
```

时才成立。

如果没有这个文件，说明你当前机器只有 `LLaMA-Factory` 导出数据，够训练，但还不够跑 repo 自己的 exact evaluator。此时有两种办法：

- 从旧机器拷回 `data/processed/xlam_fc_single_call/test.jsonl`
- 按前面的第 5 节从原始 xLAM 重建

评测命令：

```bash
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python \
  scripts/eval_llamafactory_predictions.py \
  --predictions "$RUN_DIR/generated_predictions.jsonl" \
  --processed-jsonl data/processed/xlam_fc_single_call/test.jsonl \
  --mode "$MODE"
```

## 10. 把轻量结果同步回仓库

```bash
"$CONDA_BASE/bin/conda" run -n "$ENV_NAME" python \
  scripts/summarize_run_results.py \
  --run-root "$RUN_ROOT" \
  --output-dir "results/$MACHINE_LABEL/$EXP_GROUP" \
  --machine "$MACHINE_LABEL" \
  --experiment-group "$EXP_GROUP" \
  --dataset "$EXP_GROUP" \
  --include-generated-predictions
```

## 11. 新机器训练完后，需要给我什么

最少给我下面这些：

- 你跑的是哪个模式：
  - `vanilla` / `schema_augmented` / `hammer_like`
- 你用的配置文件：
  - 例如 `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_schema_augmented_qlora_pilot1000.yaml`
- 你的 `RUN_DIR`

最好再把下面这些文件给我：

- `train_results.json`
- `predict_results.json`
- `generated_predictions.jsonl`
- `trainer_log.jsonl`
- `toolcall_eval.json`

如果你想最省事，直接把整个 `RUN_DIR` 打包给我也可以。

如果你只能给最关键的东西，优先给：

- `toolcall_eval.json`
- `train_results.json`
- 配置名

如果你那台机器没有 `data/processed/xlam_fc_single_call/test.jsonl`，那你至少把下面这些回传给我，我也能在主机器补评测：

- `generated_predictions.jsonl`
- `train_results.json`
- `predict_results.json`
- 配置名

## 最短理解

如果 repo 里已经带着 `data/llamafactory/xlam_fc_single_call/`，那新机器最短流程就是：

1. `git clone --depth 1`
2. `bash scripts/bootstrap_train_env.sh`
3. 设好 `MODE / CONFIG / RUN_DIR`
4. 跑 `llamafactory-cli train ... output_dir=...`
5. 跑完后把结果文件回传

## 12. 如果环境已经好了，这台机器现在该跑什么

这一节就是之前单独 runbook 的内容。

截至 2026-04-15，当前 direct baseline 状态：

| experiment | config | status | exact match |
| --- | --- | --- | --- |
| `vanilla pilot1000` | `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_vanilla_qlora_pilot1000.yaml` | 已完成 | `2083/2570 = 0.8105` |
| `schema_augmented pilot1000` | `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_schema_augmented_qlora_pilot1000.yaml` | 已完成 bring-up | `3984/5140 = 0.7751` |
| `hammer_like pilot1000` | `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_hammer_like_qlora_pilot1000.yaml` | 已完成 | `3983/5140 = 0.7749` |

当前阶段性判断：

- `pilot1000` 预算下，`vanilla` 暂时最好；
- `schema_augmented` 和 `hammer_like` 基本持平；
- 但这轮比较不完全公平，因为三者都固定了 `max_steps=1000`，而训练集大小不同。

当前训练集规模：

- `vanilla_train = 20588`
- `schema_augmented_train = 41176`
- `hammer_like_train = 41176`

所以当前实际 epoch：

- `vanilla = 0.3886`
- `schema_augmented = 0.1943`
- `hammer_like = 0.1943`

当前最值得补的是公平预算的 `epoch-matched 补充实验`，而不是再随便重复跑 `pilot1000`。

## 13. 多机分配规则

如果你手头只有 1 台额外机器：

- 优先跑：
  - `schema_augmented pilot2000`

如果你手头有 2 台额外机器：

- 机器 A：
  - `schema_augmented pilot2000`
- 机器 B：
  - `hammer_like pilot2000`

如果你手头有 3 台及以上额外机器：

- 前两台仍然优先跑上面两个 `pilot2000`
- 其余机器先不要随便扩别的数据集和更大模型
- 先等这两条公平预算结果回来，再决定要不要做：
  - second-seed rerun
  - held-out transfer
  - `reuse_main`

## 14. 当前标准化实验矩阵

### 14.1 已完成的 compute-matched baseline

| family | mode | config | 目的 |
| --- | --- | --- | --- |
| compute-matched | `vanilla` | `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_vanilla_qlora_pilot1000.yaml` | 当前 direct baseline 参考点 |
| compute-matched | `schema_augmented` | `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_schema_augmented_qlora_pilot1000.yaml` | 现有强 baseline bring-up |
| compute-matched | `hammer_like` | `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_hammer_like_qlora_pilot1000.yaml` | 现有强 baseline bring-up |

这组回答的是“同样 step 预算下谁更强”，当前已经够用作阶段判断，不优先再补。

### 14.2 下一步优先跑的 epoch-matched 补充实验

| family | mode | config | 目的 |
| --- | --- | --- | --- |
| epoch-matched | `schema_augmented` | `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_schema_augmented_qlora_pilot2000.yaml` | 让 `A+B` 训练覆盖度接近 `vanilla pilot1000` |
| epoch-matched | `hammer_like` | `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_hammer_like_qlora_pilot2000.yaml` | 让 `A+B` 训练覆盖度接近 `vanilla pilot1000` |

为什么是 `pilot2000`：

- 当前 `schema_augmented` / `hammer_like` 的训练集大小正好是 `vanilla` 的两倍；
- 所以把 `1000 steps` 提到 `2000 steps`，可以把 row-epoch 从约 `0.1943` 拉到约 `0.3886`；
- 这样更接近 `vanilla pilot1000` 的覆盖度。

### 14.3 当前不建议优先开的东西

除非前两组已经跑完并且结果支持继续加码，否则当前不建议先开：

- `BFCL` 当主训练集的 baseline
- 更大 backbone 的直接试跑
- multi-call / parallel-call 扩展
- 重新捡回手写 trainer

## 15. 直接可跑的补充实验命令

### 15.1 `schema_augmented pilot2000`

```bash
export MODE="schema_augmented"
export CONFIG="configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_schema_augmented_qlora_pilot2000.yaml"
export RUN_NAME="qwen25_05b_schema_augmented_qlora_pilot2000"
export RUN_DIR="$RUN_ROOT/$RUN_NAME"
mkdir -p "$RUN_DIR"

nohup "$CONDA_BASE/bin/conda" run -n "$ENV_NAME" bash -lc "
  cd '$REPO_ROOT' &&
  llamafactory-cli train '$CONFIG' output_dir='$RUN_DIR'
" > "$RUN_DIR/launch.log" 2>&1 &
```

### 15.2 `hammer_like pilot2000`

```bash
export MODE="hammer_like"
export CONFIG="configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_hammer_like_qlora_pilot2000.yaml"
export RUN_NAME="qwen25_05b_hammer_like_qlora_pilot2000"
export RUN_DIR="$RUN_ROOT/$RUN_NAME"
mkdir -p "$RUN_DIR"

nohup "$CONDA_BASE/bin/conda" run -n "$ENV_NAME" bash -lc "
  cd '$REPO_ROOT' &&
  llamafactory-cli train '$CONFIG' output_dir='$RUN_DIR'
" > "$RUN_DIR/launch.log" 2>&1 &
```
