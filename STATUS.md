# STATUS

最后更新：2026-04-13

## 论文主线

当前论文方向保持不变：

- `cross-schema decision reuse`
- 只研究 `function calling`，不扩成通用 agent framework
- 当前主线不做 `RL`
- 当前主线不做 `execution-feedback posterior distillation`

当前要验证的核心命题是：在 schema `T_A` 上学到的 decision object，能否在语义等价的 schema `T_B` 上复用。主要证据路径仍然是：

- `A->B` counterfactual decoding
- `shuffle/null` 控制组
- held-out schema transforms

主草稿：

- `2026-03-31-nips2026-function-calling-idea-draft-v2.md`

项目原则与文档规范：

- `RULES.md`
- `docs/PROJECT_RULES.md`

## 当前仓库状态

已经实现并在本机验证通过的内容：

- `pilot_v1` toy slice 的 paired-schema 数据流水线
- `LLaMA-Factory` 基线导出路径：
  - `vanilla`
  - `schema_augmented`
  - `hammer_like`
- `LLaMA-Factory` 预测输出的 exact tool-call 评估脚本：
  - `scripts/eval_llamafactory_predictions.py`
  - `src/schema_reuse/eval/toolcall.py`
- 官方 `BFCL v4` 单轮单工具 ingest / audit / export 路径：
  - `scripts/build_bfcl_v4_single_turn_slice.py`
  - `configs/bfcl_v4_single_turn/data.json`
  - `src/schema_reuse/data/bfcl_official.py`
- `BFCL` clean slice 的本机构建结果：
  - accepted `774`
  - `train=609`
  - `dev=94`
  - `test=71`
- `LLaMA-Factory` 导出现在支持 richer tool schema，并会把非标准 type 尽量归一化成 JSON Schema 近似类型
- 已删除旧的手写 baseline trainer 路径，避免仓库继续保留 smoke stub：
  - `scripts/train_*.py`
  - `src/schema_reuse/train/{direct,latent,reuse}.py`
  - `configs/pilot_v1/train/*`
  - 相关 smoke tests
- 文档入口和工程原则已经收束到：
  - `README.md`
  - `RULES.md`
  - `docs/PROJECT_RULES.md`
  - `docs/environment-repro.md`
  - `docs/README.md`
- 已验证可用的训练环境：`/root/miniconda3/envs/tooluse-llf`
- 已外置的本机产物根目录：`/root/autodl-fs/tooluse-artifacts`
  - editable `LLaMA-Factory` checkout：`/root/autodl-fs/tooluse-artifacts/external/LLaMA-Factory`
  - 本机 run 输出：`/root/autodl-fs/tooluse-artifacts/runs/local_2080ti/...`
- 适配本机 `RTX 2080 Ti 22GB` 的单卡 QLoRA 配置：
  - `configs/llamafactory/local_qwen25_05b_vanilla_qlora.yaml`
  - `configs/llamafactory/local_qwen25_05b_schema_augmented_qlora.yaml`
  - `configs/llamafactory/local_qwen25_05b_hammer_like_qlora.yaml`
- 一个 overfit sanity 配置：
  - `configs/llamafactory/local_qwen25_05b_vanilla_overfit_trainbook_qlora.yaml`
- 产物目录外置后，已经重新实际跑通一次 overfit smoke 训练，说明迁移没有把训练栈弄断

当前本机已验证版本：

- Python `3.11.15`
- PyTorch `2.6.0+cu124`
- Transformers `5.2.0`
- Datasets `4.0.0`
- Accelerate `1.11.0`
- PEFT `0.18.1`
- TRL `0.24.0`
- Bitsandbytes `0.49.2`
- LLaMA-Factory `0.9.5.dev0`
- 本机下载回退方案：`USE_MODELSCOPE_HUB=1`
- 当前已记录的新机恢复文档：
  - `docs/environment-repro.md`
- 当前已记录的精确依赖文件：
  - `requirements/train-server-validated.txt`
- 当前已记录的裸机恢复脚本：
  - `scripts/bootstrap_train_env.sh`

2026-04-12 同时已完成：

- `superpowers` skill 安装到 `~/.codex/superpowers`
- Codex skill 入口链接到 `~/.agents/skills/superpowers`

2026-04-13 新增的重要判断：

- 新增了原则四：
  - 不确定的东西先查外部做法，再决定是否推进
- 已审计外部论文/工程如何使用 `BFCL`：
  - 结论是 `BFCL` 当前更应被视为 benchmark / eval 数据，而不是默认 baseline 训练源
- 相关记录：
  - `docs/records/2026-04-13-bfcl-usage-and-baseline-data-audit.md`

## 已验证命令

默认都在仓库根目录执行。

- `python3 scripts/build_pilot_slice.py --config configs/pilot_v1/data.yaml`
  - 当前结果：写出 `data/interim/pilot_v1/candidates.jsonl`
- `python3 scripts/build_paired_dataset.py --config configs/pilot_v1/data.yaml`
  - 当前结果：写出 `data/processed/pilot_v1/{train,dev,test}.jsonl`
- `/root/miniconda3/envs/tooluse-llf/bin/python -m pytest -q`
  - 当前结果：`23 passed`
- `/root/miniconda3/envs/tooluse-llf/bin/python scripts/export_llamafactory_baselines.py`
  - 当前结果：成功导出 `data/llamafactory/pilot_v1/*`
- `BFCL_ROOT=/root/autodl-fs/tooluse-artifacts/external/gorilla/berkeley-function-call-leaderboard /root/miniconda3/envs/tooluse-llf/bin/python scripts/build_bfcl_v4_single_turn_slice.py --config configs/bfcl_v4_single_turn/data.json`
  - 当前结果：写出 `data/interim/bfcl_v4_single_turn/{candidates.jsonl,audit.json}`
- `/root/miniconda3/envs/tooluse-llf/bin/python scripts/build_paired_dataset.py --config configs/bfcl_v4_single_turn/data.json`
  - 当前结果：写出 `data/processed/bfcl_v4_single_turn/{train,dev,test}.jsonl`
- `/root/miniconda3/envs/tooluse-llf/bin/python scripts/export_llamafactory_baselines.py --processed-dir data/processed/bfcl_v4_single_turn --output-dir data/llamafactory/bfcl_v4_single_turn --dataset-prefix bfcl_v4_single_turn`
  - 当前结果：成功导出 `data/llamafactory/bfcl_v4_single_turn/*`
- `/root/miniconda3/envs/tooluse-llf/bin/python scripts/check_train_env.py`
  - 当前结果：`ready_for_real_training = true`
- `USE_MODELSCOPE_HUB=1 /root/miniconda3/envs/tooluse-llf/bin/llamafactory-cli train configs/llamafactory/local_qwen25_05b_vanilla_qlora.yaml`
  - 当前结果：训练和预测成功
- `USE_MODELSCOPE_HUB=1 /root/miniconda3/envs/tooluse-llf/bin/llamafactory-cli train configs/llamafactory/local_qwen25_05b_schema_augmented_qlora.yaml`
  - 当前结果：训练和预测成功
- `USE_MODELSCOPE_HUB=1 /root/miniconda3/envs/tooluse-llf/bin/llamafactory-cli train configs/llamafactory/local_qwen25_05b_hammer_like_qlora.yaml`
  - 当前结果：训练和预测成功
- `USE_MODELSCOPE_HUB=1 /root/miniconda3/envs/tooluse-llf/bin/llamafactory-cli train configs/llamafactory/local_qwen25_05b_vanilla_overfit_trainbook_qlora.yaml`
  - 当前结果：迁移产物目录后重新训练与预测成功
- `/root/miniconda3/envs/tooluse-llf/bin/python scripts/eval_llamafactory_predictions.py --predictions /root/autodl-fs/tooluse-artifacts/runs/local_2080ti/pilot_v1/qwen25_05b_vanilla_qlora/generated_predictions.jsonl --processed-jsonl data/processed/pilot_v1/test.jsonl --mode vanilla`
  - 当前结果：输出 exact tool-call 评估报告

## 本地实验状态

这台机器已经完成了真实的 `LLaMA-Factory` 基线打通。

详细记录：

- `docs/records/2026-04-12-local-2080ti-qlora-bringup.md`

当前最重要的实验结论：

- runtime 路径已经是真实可用的：
  - `ModelScope` 下载可用
  - `2080 Ti 22GB` 可跑 `QLoRA`
  - `qwen` template + ShareGPT tools 格式兼容
  - 预测输出可落盘并可做 exact tool-call 评估
  - exact 评估报告默认写到各 run 目录下的 `toolcall_eval.json`
- `pilot_v1` held-out 结果没有科学说服力：
  - `vanilla`：exact tool-call match `0/1`
  - `schema_augmented`：exact tool-call match `0/2`
  - `hammer_like`：exact tool-call match `0/2`
- 失败模式高度一致：
  - tool name 对
  - argument keys 对
  - argument values 错
  - 主要错误是 `departure/arrival` 角色反转
  - alias schema 样本还出现了中文值翻译：`Beijing -> 北京`、`Hangzhou -> 杭州`
- overfit sanity 检查通过：
  - `qwen25_05b_vanilla_overfit_trainbook_qlora` 达到 exact match `1/1`
  - 解释：坏结果来自 toy 数据泛化极限，而不是训练/导出/预测链路坏掉

2026-04-13 新增的工程结论：

- 官方 `BFCL v4` 的单轮单工具子集已经能在本仓库中被稳定 ingest、审计、切分、paired-transform、并导出给 `LLaMA-Factory`
- 当前本机 `BFCL` clean slice 的拒绝原因主要是：
  - `mentions_schema_surface_forms`
  - `question_not_single_user_turn`
- richer tool schema 已经保留下来，不再只导出占位式 `Argument xxx`

但 2026-04-13 同时新增了一个更重要的研究判断：

- 外部论文和工程通常把 `BFCL` 当 benchmark / evaluation 使用
- 官方 `BFCL` 评测依赖 `possible_answer` 的可接受答案集合
- 因此“把 `BFCL possible_answer` 直接压成单一 SFT target 并拿来当 baseline 主训练集”这件事，目前**不能**默认视为主线做法

## 重要边界

`pilot_v1` 仍然只是 smoke dataset。

- 它来自 toy seed，不是真正的 BFCL clean slice
- `dev` split 仍为空
- `configs/llamafactory/qwen_*` 里的 yaml 仍为了 smoke 验证而使用 `*_test` 作为 `eval_dataset`
- 新增的本机 `qwen25_05b_*` 运行结果只是工程打通证据，不是论文证据

`BFCL v4` 路径当前也有明确边界：

- `bfcl_v4_single_turn` 已经是更真实的 benchmark ingest / eval slice
- 但它现在**不是**已经确认的 baseline 默认训练源
- 当前仓库里新增的 `bfcl_v4_single_turn` 本机 QLoRA yaml 只应视为探索性配置，不应在没有进一步论证前被包装成论文主实验
- 这条边界来自：
  - 官方 `BFCL` 定位
  - `possible_answer` 的多答案评测语义
  - 对 `APIGen/xLAM`、`Hammer`、`When2Call`、`Granite` 等外部实践的审计

这些本地实验证明了：

- 基线路径在中等显卡上可跑通
- 导出格式与 `LLaMA-Factory` 兼容
- 本地会话可以端到端完成安装、训练、预测和精确评测

这些本地实验**没有**证明：

- 论文主命题
- `A->B` reuse 的科学结论
- BFCL 规模上的任何可发表结论
- `BFCL` 直接当训练主料就是合理 baseline

## 环境复现判断

当前新增的明确判断：

- 这个仓库不能假设每台机器都装了 Codex 才能工作
- 新机器恢复应该优先依赖仓库内文档和依赖文件，而不是依赖“记得当时怎么装过”
- 平台系统盘镜像 / 快照默认值得保留，但只能作为加速恢复手段，不能替代 repo 内的环境记录
- repo 内当前主维护的是裸 Linux 恢复路径，不再额外维护单独的 Docker 方案
- CUDA 版本不应被写死成所有机器唯一前提，当前改为“记录已验证版本 + 允许新机器自己决定 torch 安装方式”

相关文件：

- `docs/environment-repro.md`
- `requirements/train-server.txt`
- `requirements/train-server-validated.txt`
- `scripts/bootstrap_train_env.sh`

## 手写 trainer 清理

旧的手写 baseline trainer 已经删除。

删除原因：

- 它们不是实际训练路径，只会写出 `smoke_only_no_model` 占位结果
- baseline runtime 已经由 `LLaMA-Factory` 真实打通
- 把这类 stub 留在开源仓库里只会制造误导

当前约束：

- 不要重新引入手写 baseline trainer
- `reuse_main` 的真实训练实现仍未确定
- 方法侧实现如果未来回归，必须明确与 baseline runtime 分离

## 开源仓库约束

这个仓库要按后续 release 的开源项目维护。

- 不要把 conda 环境放在仓库目录里
- 不要把 editable 第三方源码 checkout 放在仓库目录里
- 不要把 checkpoint、预测文件、loss 图等重产物默认写进仓库目录
- 基线路径尽量复用成熟工具，当前优先复用 `LLaMA-Factory`

## 当前 source of truth

优先阅读：

- `README.md`
- `RULES.md`
- `docs/PROJECT_RULES.md`
- `STATUS.md`
- `HANDOFF.md`
- `2026-03-31-nips2026-function-calling-idea-draft-v2.md`
- `docs/records/2026-04-12-local-2080ti-qlora-bringup.md`
- `docs/records/pilot-v1-resource-estimate.md`
- `docs/records/2026-04-13-bfcl-usage-and-baseline-data-audit.md`
- `docs/llamafactory-baseline.md`

命名约定：

- 根目录 `STATUS.md` 是项目当前总状态。
- `docs/records/` 是阶段记录和实验记录。

## 下一步建议

1. 优先检查 `Salesforce/xlam-function-calling-60k` 是否能无损映射到当前 paired-schema 流水线。
2. 如果 `xLAM/APIGen` 可用，先把它接成 baseline 训练源。
3. 把 `BFCL` 保持为 benchmark / eval slice，不要先把 benchmark 和训练源混在一起。
4. 继续用 `LLaMA-Factory` 跑 baseline，不要回头扩手写 trainer。
5. 对所有后续预测输出统一跑 exact tool-call evaluator，不再用 BLEU/ROUGE 代替函数调用正确性。
6. 只有 baseline 训练源和 held-out benchmark 分工稳定后，才讨论 `reuse_main` 的训练实现。
