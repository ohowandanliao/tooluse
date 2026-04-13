# HANDOFF

这个文件是给下一次接手机器或会话的人看的，目标是尽快接管仓库，不重复踩坑。

写入时仓库目标仍然是：

- branch：`main`
- remote：`origin`
- 默认推送目标：`origin/main`

## 阅读顺序

按这个顺序读：

1. `README.md`
2. `RULES.md`
3. `docs/PROJECT_RULES.md`
4. `STATUS.md`
5. `2026-03-31-nips2026-function-calling-idea-draft-v2.md`
6. `docs/records/2026-04-12-local-2080ti-qlora-bringup.md`
7. `docs/records/2026-04-13-bfcl-usage-and-baseline-data-audit.md`
8. `docs/environment-repro.md`
9. `docs/llamafactory-baseline.md`

## 这个项目真正要证明什么

当前论文**不是**在做：

- 通用 agent framework
- 把 `RL` 当标题方法
- 把 feedback posterior distillation 当主贡献

当前论文**是在做**：

- `schema-reusable decision representation`
- 用 `A->B` counterfactual decoding 证明复用
- 证明 `A->B > shuffle/null`
- 检查收益能否在 held-out schema transform 下保留

执行过程中必须同时遵守：

- `RULES.md`
- `docs/PROJECT_RULES.md`
- 特别是新增的原则四：
  - 不确定的东西先查外部做法，再决定是否推进

命名约定：

- 根目录 `STATUS.md` 是总状态总览。
- `docs/records/` 是阶段性记录，不再使用容易混淆的 `docs/status/`。
- 历史计划文档可能提到已删除的手写 trainer 文件，以当前代码和 `STATUS.md` 为准。

## baseline 的实际 runtime 路径

现在正确的 baseline 路径是：

- 先把处理后的 paired-schema 样本导出成 `LLaMA-Factory` 数据集
- 再用 `llamafactory-cli` 跑 baseline SFT / QLoRA

关键文件：

- `README.md`
- `docs/PROJECT_RULES.md`
- `src/schema_reuse/export/llamafactory.py`
- `scripts/export_llamafactory_baselines.py`
- `scripts/eval_llamafactory_predictions.py`
- `configs/llamafactory/qwen_vanilla_sft_lora.yaml`
- `configs/llamafactory/qwen_schema_augmented_sft_lora.yaml`
- `configs/llamafactory/qwen_hammer_like_lora.yaml`
- `configs/llamafactory/local_qwen25_05b_vanilla_qlora.yaml`
- `configs/llamafactory/local_qwen25_05b_schema_augmented_qlora.yaml`
- `configs/llamafactory/local_qwen25_05b_hammer_like_qlora.yaml`
- `scripts/build_bfcl_v4_single_turn_slice.py`
- `configs/bfcl_v4_single_turn/data.json`
- `docs/llamafactory-baseline.md`
- `tests/export/test_llamafactory.py`
- `tests/eval/test_toolcall.py`

文档层面的固定入口现在已经明确：

- 对外入口看 `README.md`
- 用户原则先看 `RULES.md`
- 项目原则和文档放置规则再看 `docs/PROJECT_RULES.md`
- 新机器恢复路径看 `docs/environment-repro.md`
- 文档地图看 `docs/README.md`

## 当前本地环境

这台机器上已经有验证通过的环境：

- env 路径：`/root/miniconda3/envs/tooluse-llf`
- 本机产物根目录：`/root/autodl-fs/tooluse-artifacts`
- editable `LLaMA-Factory` checkout：`/root/autodl-fs/tooluse-artifacts/external/LLaMA-Factory`
- 2026-04-12 可用的下载回退：`USE_MODELSCOPE_HUB=1`
- bring-up 时使用的本地 backbone cache：
  - `/root/.cache/modelscope/hub/models/Qwen/Qwen2___5-0___5B-Instruct`

这个环境的已验证版本：

- Python `3.11.15`
- PyTorch `2.6.0+cu124`
- Transformers `5.2.0`
- Datasets `4.0.0`
- Accelerate `1.11.0`
- PEFT `0.18.1`
- TRL `0.24.0`
- Bitsandbytes `0.49.2`
- LLaMA-Factory `0.9.5.dev0`

补充说明：

- editable `LLaMA-Factory` checkout 和 run 目录迁到仓库外后，已经重新跑过一次 `local_qwen25_05b_vanilla_overfit_trainbook_qlora`
- 结果仍然是训练成功、预测成功、exact tool-call `1/1`
- 2026-04-13 还额外 clone 了官方 `gorilla` 仓库到：
  - `/root/autodl-fs/tooluse-artifacts/external/gorilla`
  - 这里只用于读取官方 `BFCL` 数据和评测实现，不在仓库内提交
- 2026-04-13 已补充新机器恢复文档和精确依赖文件：
  - `docs/environment-repro.md`
  - `requirements/train-server-validated.txt`
- 2026-04-13 额外补充了裸 Linux 恢复脚本：
  - `scripts/bootstrap_train_env.sh`

## 当前 toy 数据

- `data/interim/pilot_v1/candidates.jsonl`
- `data/processed/pilot_v1/train.jsonl`
- `data/processed/pilot_v1/dev.jsonl`
- `data/processed/pilot_v1/test.jsonl`
- `data/llamafactory/pilot_v1/`

## 当前 BFCL ingest 状态

已在仓库内打通：

- `data/interim/bfcl_v4_single_turn/candidates.jsonl`
- `data/interim/bfcl_v4_single_turn/audit.json`
- `data/processed/bfcl_v4_single_turn/{train,dev,test}.jsonl`
- `data/llamafactory/bfcl_v4_single_turn/`

本机当前结果：

- accepted `774`
- `train=609`
- `dev=94`
- `test=71`

注意这里的定位：

- 这是 `BFCL` benchmark ingest / clean eval slice
- 当前**不要**默认把它视为 baseline 主训练源
- 理由见：
  - `docs/records/2026-04-13-bfcl-usage-and-baseline-data-audit.md`

## 2026-04-12 实际跑过什么

成功的本地 baseline run：

- `/root/autodl-fs/tooluse-artifacts/runs/local_2080ti/pilot_v1/qwen25_05b_vanilla_qlora`
- `/root/autodl-fs/tooluse-artifacts/runs/local_2080ti/pilot_v1/qwen25_05b_schema_augmented_qlora`
- `/root/autodl-fs/tooluse-artifacts/runs/local_2080ti/pilot_v1/qwen25_05b_hammer_like_qlora`

sanity overfit run：

- `/root/autodl-fs/tooluse-artifacts/runs/local_2080ti/pilot_v1/qwen25_05b_vanilla_overfit_trainbook_qlora`

这些结果要这样理解：

- 三个 held-out toy baseline 的 exact tool-call 都是 `0`
- tool names 和 argument keys 是对的
- values 是错的
- 最常见错误是 `departure/arrival` 反转
- alias schema 样本里还出现了中文值翻译
- overfit sanity run 是 `1/1`

结论：

- 训练、导出、template、预测链路是通的
- toy split 太小也太薄，不能支持科学结论
- 不要把 BLEU/ROUGE 当 function-calling correctness

## 精确评测现在怎么做

仓库里已经有 exact tool-call evaluator，不需要再人工盯预测文本。

核心文件：

- `scripts/eval_llamafactory_predictions.py`
- `src/schema_reuse/eval/toolcall.py`

示例：

```bash
/root/miniconda3/envs/tooluse-llf/bin/python scripts/eval_llamafactory_predictions.py \
  --predictions /root/autodl-fs/tooluse-artifacts/runs/local_2080ti/pilot_v1/qwen25_05b_vanilla_qlora/generated_predictions.jsonl \
  --processed-jsonl data/processed/pilot_v1/test.jsonl \
  --mode vanilla
```

输出会给出：

- parsed prediction rate
- exact tool-call match
- tool-name match
- argument-key exact match
- argument-value exact match
- 如果提供 processed metadata，还会给 schema variant 和 transform family 分组结果
- 默认报告文件名是和 `generated_predictions.jsonl` 同目录的 `toolcall_eval.json`

## 手写 trainer 路径已经移除

旧的手写 baseline trainer 已经从代码库删除。

原因：

- 它们只是 smoke stub，不是真实训练实现
- `LLaMA-Factory` 已经是经过本机验证的 baseline runtime
- 对外 release 时继续保留这条路径只会误导使用者

后续不要做的事：

- 不要把这条手写 baseline 路径加回来
- 不要把 `reuse_main` 的方法侧探索误包装成 baseline runtime

## 已验证命令

默认在仓库根目录执行。

### 数据流水线

```bash
python3 scripts/build_pilot_slice.py --config configs/pilot_v1/data.yaml
python3 scripts/build_paired_dataset.py --config configs/pilot_v1/data.yaml
```

### 测试

```bash
/root/miniconda3/envs/tooluse-llf/bin/python -m pytest -q
```

2026-04-12 删除手写 trainer 后的预期结果：

- `23 passed`

### baseline 导出

```bash
/root/miniconda3/envs/tooluse-llf/bin/python scripts/export_llamafactory_baselines.py
```

2026-04-12 的预期结果：

- 正常导出到 `data/llamafactory/pilot_v1`
- `pilot_v1/dev.jsonl` 为空，所以 `*_eval.json` 为空是正常的

### BFCL ingest

```bash
BFCL_ROOT=/root/autodl-fs/tooluse-artifacts/external/gorilla/berkeley-function-call-leaderboard \
  /root/miniconda3/envs/tooluse-llf/bin/python scripts/build_bfcl_v4_single_turn_slice.py \
  --config configs/bfcl_v4_single_turn/data.json

/root/miniconda3/envs/tooluse-llf/bin/python scripts/build_paired_dataset.py \
  --config configs/bfcl_v4_single_turn/data.json

/root/miniconda3/envs/tooluse-llf/bin/python scripts/export_llamafactory_baselines.py \
  --processed-dir data/processed/bfcl_v4_single_turn \
  --output-dir data/llamafactory/bfcl_v4_single_turn \
  --dataset-prefix bfcl_v4_single_turn
```

2026-04-13 的预期结果：

- 写出 `data/interim/bfcl_v4_single_turn/audit.json`
- 写出 `data/processed/bfcl_v4_single_turn/{train,dev,test}.jsonl`
- 写出 `data/llamafactory/bfcl_v4_single_turn/*`

### 训练环境探针

```bash
/root/miniconda3/envs/tooluse-llf/bin/python scripts/check_train_env.py
```

2026-04-12 的预期结果：

- `ready_for_real_training = true`

### 新机器恢复

优先阅读：

- `docs/environment-repro.md`

核心文件：

- `requirements/train-server.txt`
- `requirements/train-server-validated.txt`
- `scripts/bootstrap_train_env.sh`

当前判断：

- 可以默认保存系统盘镜像 / 快照作为快速恢复手段
- 但不要把它当成唯一环境记录
- repo 内必须保留可审计的依赖、commit、命令和验证步骤
- 当前主维护的是裸 Linux 恢复路径，不单独维护 Docker 路径

### 本地 GPU bring-up

```bash
USE_MODELSCOPE_HUB=1 /root/miniconda3/envs/tooluse-llf/bin/llamafactory-cli train \
  configs/llamafactory/local_qwen25_05b_vanilla_qlora.yaml

USE_MODELSCOPE_HUB=1 /root/miniconda3/envs/tooluse-llf/bin/llamafactory-cli train \
  configs/llamafactory/local_qwen25_05b_schema_augmented_qlora.yaml

USE_MODELSCOPE_HUB=1 /root/miniconda3/envs/tooluse-llf/bin/llamafactory-cli train \
  configs/llamafactory/local_qwen25_05b_hammer_like_qlora.yaml
```

## 下一位接手的人应该做什么

按顺序做：

1. 保持论文范围收窄，不要漂移回 framework 叙事。
2. 先读 `docs/records/2026-04-13-bfcl-usage-and-baseline-data-audit.md`，不要默认把 `BFCL` 当 baseline 训练源。
3. 优先检查 `Salesforce/xlam-function-calling-60k` 是否能接入当前 paired-schema 流水线。
4. 如果 `xLAM/APIGen` 可用，先把它接成 baseline 训练源。
5. 把 `BFCL` 保持为 benchmark / eval slice，并对所有预测输出统一跑 exact evaluator。
6. 只有 baseline 训练源和 held-out benchmark 的分工稳定后，才重新讨论 `reuse_main` 的训练实现。

## 明确不要做什么

不要：

- 把 `pilot_v1` 结果说成论文证据
- 用 BLEU/ROUGE 代替函数调用正确率
- 重新引入手写 baseline trainer
- 因为后期可能会用就提前把 `RL` 拉回主线
- 把论文叙事重新扩回 tool-use framework
- 在没有进一步论证前，把 `BFCL possible_answer` 直接压成单一训练 target 然后包装成默认 baseline 主线

## 如果需要服务器

参考：

- `docs/records/pilot-v1-resource-estimate.md`
- `requirements/train-server.txt`

当前建议仍然是：

- 优选：`1x A100 80GB` 或 `1x H100 80GB`
- 也能做但更紧：强一点的 `48GB` GPU

这台本地 `2080 Ti 22GB` 机器适合工程打通和很小的 QLoRA 实验，不适合真实论文矩阵。
