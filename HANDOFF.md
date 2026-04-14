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
5. `results/README.md`
6. `results/local_2080ti/pilot_v1/README.md`
7. `2026-03-31-nips2026-function-calling-idea-draft-v2.md`
8. `docs/records/2026-04-12-local-2080ti-qlora-bringup.md`
9. `docs/records/2026-04-13-bfcl-usage-and-baseline-data-audit.md`
10. `docs/records/2026-04-14-paper-progress-and-next-steps.md`
11. `docs/records/2026-04-14-xlam-fc60k-ingest-audit.md`
12. `docs/environment-repro.md`
13. `docs/llamafactory-baseline.md`
14. `docs/new-machine-quickstart.md`

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
- 以及新增的原则五：
  - 仓库内要保留可复现实验证据，但不提交权重
- 以及新增的原则六：
  - 如果需要，可以整理 prompt 让用户去问 `GPT-5.4-pro` 做扩展或纠偏
- 以及新增的原则七：
  - 做外部检索时，尽量优先更新的资料；旧资料要么够新，要么够硬

命名约定：

- 根目录 `STATUS.md` 是总状态总览。
- `docs/records/` 是阶段性记录，不再使用容易混淆的 `docs/status/`。
- 历史计划文档可能提到已删除的手写 trainer 文件，以当前代码和 `STATUS.md` 为准。
- 如果某次关键决策明显参考了外部 `GPT-5.4-pro` 回答，也要把 prompt 用途和采纳点写回仓库文档，而不是只留在聊天记录里。
- 做外部检索时，默认优先看 `2025` 年及以后的资料；如果必须回退到更早文献，优先保留高影响力和官方来源。

当前新增的关键阶段判断：

- 项目现在已经不是“baseline runtime 不通”
- 项目现在也还不是“主论文实验已经开始批量跑”
- 更准确地说，当前处于：
  - `baseline runtime ready`
  - `paper evidence not ready`
- 这条判断的完整解释见：
  - `docs/records/2026-04-14-paper-progress-and-next-steps.md`

当前新增的外部 challenge 整合判断：

- `docs/fc_pdf/function-calling-paper-evaluation.md` 的核心结论已经被吸收进仓库决策
- 当前明确采纳：
  - `schema_augmented` 是强 baseline，不是主创新
  - 主路线仍是 `C = schema-reusable decision representation`
  - fallback 是 `B = held-out schema transfer / evaluation paper`
- 当前工作判据已经被收紧为：
  - kill 倾向：
    - best baseline retention `>= 0.93`
    - 或关闭 `>= 80%` transfer gap
  - go 倾向：
    - `vanilla` held-out gap `>= 12` 点
    - 且最强 baseline 仍保留 `>= 6~8` 点 gap
  - `reuse_main` 的主证明协议里，`decoder` 应优先不看原始 `x`
  - `shuffle/null` controls 不是可选项
- 整合版记录见：
  - `docs/records/2026-04-14-external-paper-eval-synthesis.md`

当前新增的数据侧判断：

- `xLAM function-calling-60k` 已经完成真实全量数据的 ingest / paired / export
- 当前 clean single-answer slice 结果：
  - raw `60000`
  - accepted `25711`
  - rejected `34289`
  - `train=20588`
  - `dev=2553`
  - `test=2570`
- 真实文件还暴露了一个兼容点：
  - `id` 是整数，不是字符串
  - 仓库已修复为统一转成字符串 `sample_id`
- 这条边界的完整解释见：
  - `docs/records/2026-04-14-xlam-fc60k-ingest-audit.md`

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
- `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_vanilla_qlora_pilot1000.yaml`
- `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_schema_augmented_qlora_pilot1000.yaml`
- `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_hammer_like_qlora_pilot1000.yaml`
- `scripts/build_bfcl_v4_single_turn_slice.py`
- `scripts/build_xlam_fc_single_call_slice.py`
- `configs/bfcl_v4_single_turn/data.json`
- `configs/xlam_fc_single_call/data.json`
- `docs/llamafactory-baseline.md`
- `tests/export/test_llamafactory.py`
- `tests/eval/test_toolcall.py`

文档层面的固定入口现在已经明确：

- 对外入口看 `README.md`
- 用户原则先看 `RULES.md`
- 项目原则和文档放置规则再看 `docs/PROJECT_RULES.md`
- 实验结果证据入口看 `results/README.md`
- 新机器恢复路径看 `docs/environment-repro.md`
- 如果只想最短开跑路径，先看 `docs/new-machine-quickstart.md`
  - 里面已经补了 `vanilla / schema_augmented / hammer_like` 的训练与评测命令
  - 当前默认建议是“每台机器只跑一个 baseline 配方”，不要把三条都堆到同一台新机器上
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
- `pypdf 6.10.0`

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
- 2026-04-13 额外补充了仓库内实验结果证据目录：
  - `results/local_2080ti/pilot_v1/README.md`
  - `results/local_2080ti/pilot_v1/commands.md`
  - `results/local_2080ti/pilot_v1/manifest.json`
- 2026-04-14 为了读取本机外部 PDF 调研材料，向当前环境临时安装了：
  - `pypdf`
  - 这不是 repo 训练链路的必需依赖

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

## 当前 xLAM ingest 状态

已在仓库内打通：

- `data/interim/xlam_fc_single_call/candidates.jsonl`
- `data/interim/xlam_fc_single_call/audit.json`
- `data/processed/xlam_fc_single_call/{train,dev,test}.jsonl`
- `data/llamafactory/xlam_fc_single_call/`

本机当前结果：

- raw `60000`
- accepted `25711`
- rejected `34289`
- rejection reasons：
  - `not_single_answer=31539`
  - `mentions_schema_surface_forms=2750`
- `train=20588`
- `dev=2553`
- `test=2570`

注意这里的定位：

- 这是当前 repo 里更像“真实 baseline 训练主线”的数据源
- 但当前仓库仍然只接了 `single-answer` clean slice
- multi-call / parallel-call 不是这一步的主线，后续是否扩展要看 real-data baseline 结果
- 2026-04-14 当前已经起了一条 real-data run：
  - config：`configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_vanilla_qlora_pilot1000.yaml`
  - output：`/root/autodl-fs/tooluse-artifacts/runs/local_2080ti/xlam_fc_single_call/qwen25_05b_vanilla_qlora_pilot1000`
  - 如果接手时它已经结束，下一步先跑 exact evaluator，再把轻量结果同步回 `results/`

## 当前 xLAM baseline 运行进度

当前只启动了一个真实 `xLAM` baseline：

- 配置：
  - `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_vanilla_qlora_pilot1000.yaml`
- run 目录：
  - `/root/autodl-fs/tooluse-artifacts/runs/local_2080ti/xlam_fc_single_call/qwen25_05b_vanilla_qlora_pilot1000`

截至 2026-04-14 本轮最后一次观察：

- 训练已完成：
  - `train_loss=0.0520`
  - `train_runtime=3255.909s`
- 预测还没结束：
  - `launch.log` 已到 `2563/2570`
  - `generated_predictions.jsonl` 还没出现
  - `predict_results.json` 还没出现
  - `toolcall_eval.json` 还没出现
- 当前没有并行开第二个 xLAM baseline：
  - `schema_augmented` 未启动
  - `hammer_like` 未启动

接手后优先动作：

1. 先确认这个 `vanilla` prediction 是否正常结束。
2. 结束后立刻跑 exact evaluator。
3. 把轻量结果同步进 `results/local_2080ti/xlam_fc_single_call/`。
4. 如果有新机器，把 `schema_augmented` / `hammer_like` 拆到别的机器；只有没有额外机器时才考虑串行排队。

## 2026-04-12 实际跑过什么

成功的本地 baseline run：

- `/root/autodl-fs/tooluse-artifacts/runs/local_2080ti/pilot_v1/qwen25_05b_vanilla_qlora`
- `/root/autodl-fs/tooluse-artifacts/runs/local_2080ti/pilot_v1/qwen25_05b_schema_augmented_qlora`
- `/root/autodl-fs/tooluse-artifacts/runs/local_2080ti/pilot_v1/qwen25_05b_hammer_like_qlora`

sanity overfit run：

- `/root/autodl-fs/tooluse-artifacts/runs/local_2080ti/pilot_v1/qwen25_05b_vanilla_overfit_trainbook_qlora`

仓库内证据位置：

- `results/local_2080ti/pilot_v1/commands.md`
- `results/local_2080ti/pilot_v1/manifest.json`
- `results/local_2080ti/pilot_v1/qwen25_05b_vanilla_qlora/`
- `results/local_2080ti/pilot_v1/qwen25_05b_schema_augmented_qlora/`
- `results/local_2080ti/pilot_v1/qwen25_05b_hammer_like_qlora/`
- `results/local_2080ti/pilot_v1/qwen25_05b_vanilla_overfit_trainbook_qlora/`

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

- `29 passed`

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

### xLAM ingest

```bash
XLAM_FC_ROOT=/root/autodl-fs/tooluse-artifacts/external/xlam \
  /root/miniconda3/envs/tooluse-llf/bin/python scripts/build_xlam_fc_single_call_slice.py \
  --config configs/xlam_fc_single_call/data.json

/root/miniconda3/envs/tooluse-llf/bin/python scripts/build_paired_dataset.py \
  --config configs/xlam_fc_single_call/data.json

/root/miniconda3/envs/tooluse-llf/bin/python scripts/export_llamafactory_baselines.py \
  --processed-dir data/processed/xlam_fc_single_call \
  --output-dir data/llamafactory/xlam_fc_single_call \
  --dataset-prefix xlam_fc_single_call
```

2026-04-14 的预期结果：

- 写出 `data/interim/xlam_fc_single_call/audit.json`
- 写出 `data/processed/xlam_fc_single_call/{train,dev,test}.jsonl`
- 写出 `data/llamafactory/xlam_fc_single_call/*`

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
4. 这一步现在已经完成：
   - `xLAM` full-data ingest / paired / export 已跑通
5. 现在直接进入 real-data baseline 阶段，优先把 `vanilla / schema_augmented / hammer_like` 拆到不同机器上做出来。
6. 把 `BFCL` 保持为 benchmark / eval slice，并对所有预测输出统一跑 exact evaluator。
7. 只有真实 held-out baseline 结果已经说明 direct recipe 仍然不够时，才重新讨论 `reuse_main` 的训练实现。

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
