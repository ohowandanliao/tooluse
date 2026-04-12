# STATUS

最后更新：2026-04-12

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
- 已删除旧的手写 baseline trainer 路径，避免仓库继续保留 smoke stub：
  - `scripts/train_*.py`
  - `src/schema_reuse/train/{direct,latent,reuse}.py`
  - `configs/pilot_v1/train/*`
  - 相关 smoke tests
- 文档入口和工程原则已经收束到：
  - `README.md`
  - `docs/PROJECT_RULES.md`
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

2026-04-12 同时已完成：

- `superpowers` skill 安装到 `~/.codex/superpowers`
- Codex skill 入口链接到 `~/.agents/skills/superpowers`

## 已验证命令

默认都在仓库根目录执行。

- `python3 scripts/build_pilot_slice.py --config configs/pilot_v1/data.yaml`
  - 当前结果：写出 `data/interim/pilot_v1/candidates.jsonl`
- `python3 scripts/build_paired_dataset.py --config configs/pilot_v1/data.yaml`
  - 当前结果：写出 `data/processed/pilot_v1/{train,dev,test}.jsonl`
- `/root/miniconda3/envs/tooluse-llf/bin/python -m pytest -q`
  - 当前结果：`17 passed`
- `/root/miniconda3/envs/tooluse-llf/bin/python scripts/export_llamafactory_baselines.py`
  - 当前结果：成功导出 `data/llamafactory/pilot_v1/*`
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

## 重要边界

`pilot_v1` 仍然只是 smoke dataset。

- 它来自 toy seed，不是真正的 BFCL clean slice
- `dev` split 仍为空
- `configs/llamafactory/qwen_*` 里的 yaml 仍为了 smoke 验证而使用 `*_test` 作为 `eval_dataset`
- 新增的本机 `qwen25_05b_*` 运行结果只是工程打通证据，不是论文证据

这些本地实验证明了：

- 基线路径在中等显卡上可跑通
- 导出格式与 `LLaMA-Factory` 兼容
- 本地会话可以端到端完成安装、训练、预测和精确评测

这些本地实验**没有**证明：

- 论文主命题
- `A->B` reuse 的科学结论
- BFCL 规模上的任何可发表结论

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
- `docs/PROJECT_RULES.md`
- `STATUS.md`
- `HANDOFF.md`
- `2026-03-31-nips2026-function-calling-idea-draft-v2.md`
- `docs/records/2026-04-12-local-2080ti-qlora-bringup.md`
- `docs/records/deepresearch-status.md`
- `docs/records/pilot-v1-resource-estimate.md`
- `docs/llamafactory-baseline.md`

命名约定：

- 根目录 `STATUS.md` 是项目当前总状态。
- `docs/records/` 是阶段记录和实验记录。

## 下一步建议

1. 构建一个真正来自 BFCL 的 clean single-turn slice，并严格处理 split hygiene。
2. 把这个真实 slice 导出到新的 `data/llamafactory/<dataset_name>` 目录。
3. 继续用 `LLaMA-Factory` 跑 baseline，不要回头扩手写 trainer。
4. 对所有后续预测输出统一跑 exact tool-call evaluator，不再用 BLEU/ROUGE 代替函数调用正确性。
5. 先在真实 slice 上重跑三类 baseline：
   - `vanilla`
   - `schema_augmented`
   - `hammer_like`
6. 只有在真实 baseline 稳定后，才讨论 `reuse_main` 的训练实现。
