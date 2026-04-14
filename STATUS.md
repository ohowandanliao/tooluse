# STATUS

最后更新：2026-04-14

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
- `counterfactual` 指标聚合工具还只到占位阶段：
  - `scripts/eval_counterfactual.py`
  - `src/schema_reuse/eval/counterfactual.py`
- 官方 `BFCL v4` 单轮单工具 ingest / audit / export 路径：
  - `scripts/build_bfcl_v4_single_turn_slice.py`
  - `configs/bfcl_v4_single_turn/data.json`
  - `src/schema_reuse/data/bfcl_official.py`
- `xLAM function-calling-60k` 的本地 ingest / audit / export 路径已经在真实全量数据上跑通：
  - `scripts/build_xlam_fc_single_call_slice.py`
  - `configs/xlam_fc_single_call/data.json`
  - `src/schema_reuse/data/xlam_official.py`
- `xLAM` single-answer clean slice 的本机构建结果：
  - raw `60000`
  - accepted `25711`
  - rejected `34289`
  - rejection reasons：
    - `not_single_answer=31539`
    - `mentions_schema_surface_forms=2750`
  - `train=20588`
  - `dev=2553`
  - `test=2570`
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
  - `results/README.md`
  - `docs/environment-repro.md`
  - `docs/README.md`
- 已补充仓库内实验结果证据目录：
  - `results/local_2080ti/pilot_v1/README.md`
  - `results/local_2080ti/pilot_v1/commands.md`
  - `results/local_2080ti/pilot_v1/manifest.json`
- 已新增论文推进判断记录：
  - `docs/records/2026-04-14-paper-progress-and-next-steps.md`
- 已新增 `xLAM` 接入审计记录：
  - `docs/records/2026-04-14-xlam-fc60k-ingest-audit.md`
- 已验证可用的训练环境：`/root/miniconda3/envs/tooluse-llf`
- 已外置的本机产物根目录：`/root/autodl-fs/tooluse-artifacts`
  - editable `LLaMA-Factory` checkout：`/root/autodl-fs/tooluse-artifacts/external/LLaMA-Factory`
  - 本机 run 输出：`/root/autodl-fs/tooluse-artifacts/runs/local_2080ti/...`
- 适配本机 `RTX 2080 Ti 22GB` 的单卡 QLoRA 配置：
  - `configs/llamafactory/local_qwen25_05b_vanilla_qlora.yaml`
  - `configs/llamafactory/local_qwen25_05b_schema_augmented_qlora.yaml`
  - `configs/llamafactory/local_qwen25_05b_hammer_like_qlora.yaml`
- 面向 `xLAM` real-data pilot 的单卡 QLoRA 配置：
  - `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_vanilla_qlora_pilot1000.yaml`
  - `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_schema_augmented_qlora_pilot1000.yaml`
  - `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_hammer_like_qlora_pilot1000.yaml`
- 已新增新机器最短启动文档：
  - `docs/new-machine-quickstart.md`
  - 已补充 `vanilla / schema_augmented / hammer_like` 三条训练与评测命令
  - 默认建议改为“每台机器只跑一个 baseline 配方”，用于分担多机实验压力
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
- `pypdf 6.10.0` 已临时装入当前环境，用于读取本机外部 PDF 调研材料；它不是当前 repo 训练链路的必需依赖
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
- 新增了原则五：
  - 仓库内要保留可复现实验证据，但不提交权重
- 新增了原则六：
  - 如果需要，可以整理 prompt 让用户去问 `GPT-5.4-pro` 做扩展或纠偏
- 新增了原则七：
  - 做外部检索时，尽量优先更新的资料；旧资料要么够新，要么够硬
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
  - 当前结果：`29 passed`
- `/root/miniconda3/envs/tooluse-llf/bin/python scripts/export_llamafactory_baselines.py`
  - 当前结果：成功导出 `data/llamafactory/pilot_v1/*`
- `XLAM_FC_ROOT=/root/autodl-fs/tooluse-artifacts/external/xlam /root/miniconda3/envs/tooluse-llf/bin/python scripts/build_xlam_fc_single_call_slice.py --config configs/xlam_fc_single_call/data.json`
  - 当前结果：写出 `data/interim/xlam_fc_single_call/{candidates.jsonl,audit.json}`
- `/root/miniconda3/envs/tooluse-llf/bin/python scripts/build_paired_dataset.py --config configs/xlam_fc_single_call/data.json`
  - 当前结果：写出 `data/processed/xlam_fc_single_call/{train,dev,test}.jsonl`
- `/root/miniconda3/envs/tooluse-llf/bin/python scripts/export_llamafactory_baselines.py --processed-dir data/processed/xlam_fc_single_call --output-dir data/llamafactory/xlam_fc_single_call --dataset-prefix xlam_fc_single_call`
  - 当前结果：成功导出 `data/llamafactory/xlam_fc_single_call/*`
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
- `/root/miniconda3/envs/tooluse-llf/bin/python scripts/summarize_run_results.py --run-root /root/autodl-fs/tooluse-artifacts/runs/local_2080ti/pilot_v1 --output-dir results/local_2080ti/pilot_v1 --machine local_2080ti --experiment-group pilot_v1 --dataset pilot_v1 --include-generated-predictions`
  - 当前结果：把轻量实验结果证据同步回仓库 `results/local_2080ti/pilot_v1`
- `/root/miniconda3/envs/tooluse-llf/bin/python scripts/eval_llamafactory_predictions.py --predictions /root/autodl-fs/tooluse-artifacts/runs/local_2080ti/xlam_fc_single_call/qwen25_05b_vanilla_qlora_pilot1000/generated_predictions.jsonl --processed-jsonl data/processed/xlam_fc_single_call/test.jsonl --mode vanilla`
  - 当前结果：`xLAM vanilla pilot1000` exact tool-call `2083/2570 = 0.8105`
- `/root/miniconda3/envs/tooluse-llf/bin/python scripts/summarize_run_results.py --run-root /root/autodl-fs/tooluse-artifacts/runs/local_2080ti/xlam_fc_single_call --output-dir results/local_2080ti/xlam_fc_single_call --machine local_2080ti --experiment-group xlam_fc_single_call --dataset xlam_fc_single_call --include-generated-predictions`
  - 当前结果：把 `xLAM vanilla pilot1000` 轻量结果证据同步回仓库 `results/local_2080ti/xlam_fc_single_call`

## 本地实验状态

这台机器已经完成了真实的 `LLaMA-Factory` 基线打通。

详细记录：

- `docs/records/2026-04-12-local-2080ti-qlora-bringup.md`
- `results/local_2080ti/pilot_v1/README.md`
- `results/local_2080ti/pilot_v1/manifest.json`
- `results/local_2080ti/pilot_v1/commands.md`

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

2026-04-14 新增的项目阶段判断：

- 当前项目状态更准确地说是：
  - `baseline runtime ready`
  - `paper evidence not ready`
- 当前最缺的不是再多跑 `pilot_v1`，而是：
  - 真实 baseline 训练源
  - 真实 held-out schema baseline 结果
  - 真实可判决的 `reuse_main` / `A->B` / `shuffle/null` 接口
- 相关记录：
  - `docs/records/2026-04-14-paper-progress-and-next-steps.md`
  - `docs/records/2026-04-14-external-paper-eval-synthesis.md`
- 当前 `xLAM vanilla pilot1000` 真实运行状态：
  - 配置：
    - `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_vanilla_qlora_pilot1000.yaml`
  - run 目录：
    - `/root/autodl-fs/tooluse-artifacts/runs/local_2080ti/xlam_fc_single_call/qwen25_05b_vanilla_qlora_pilot1000`
  - 当前状态：
    - 训练已完成
    - 预测已完成
    - exact evaluator 已完成
    - 轻量结果证据已同步回仓库
  - 当前关键指标：
    - `train_loss=0.0520`
    - `train_runtime=3255.909s`
    - `predict_runtime=9178.2133s`
    - `parsed_prediction_rate=0.9938`
    - `exact_match_rate=0.8105`
    - `exact_match_count=2083/2570`
    - `name_match_rate=0.9938`
    - `argument_key_exact_match_rate=0.8949`
    - `argument_value_exact_match_rate=0.8105`
  - 仓库内证据：
    - `results/local_2080ti/xlam_fc_single_call/manifest.json`
    - `results/local_2080ti/xlam_fc_single_call/qwen25_05b_vanilla_qlora_pilot1000/`
  - 当前只完成了 `vanilla`
    - `schema_augmented` 和 `hammer_like` 还未开始

2026-04-14 新增的外部 challenge 整合判断：

- 已把 `docs/fc_pdf/function-calling-paper-evaluation.md` 的核心判断整合进仓库记录：
  - `schema_augmented` 只应视为强 baseline / recipe，不足以单独支撑当前 NeurIPS 2026 主线
  - 当前主路线仍是：
    - `C = schema-reusable decision representation`
  - 当前 fallback 是：
    - `B = held-out schema transfer / evaluation paper`
- 当前采纳的 kill/go 工作判据：
  - kill 倾向：
    - best baseline retention `>= 0.93`
    - 或 best baseline 关闭 `>= 80%` transfer gap
  - go 倾向：
    - `vanilla` 的 held-out gap `>= 12` 个点
    - 且最强 baseline 仍保留 `>= 6~8` 个点 gap
- 当前主协议进一步收紧为：
  - `reuse_main` 的主证明应优先采用 `decoder` 不看原始 `x` 的 fixed-`d` `A->B` schema swap
  - `shuffle/null` controls 不是可选项
- 相关记录：
  - `docs/records/2026-04-14-external-paper-eval-synthesis.md`

2026-04-14 新增的数据侧进展：

- 已基于真实本地文件跑通 `xLAM function-calling-60k` 的单轮 single-answer ingest / audit / export
- 当前支持解析：
  - `id`
  - `query`
  - `tools`
  - `answers`
- 真实全量文件观察到的额外事实：
  - 顶层 payload 是 `list[60000]`
  - `id` 是整数，不是字符串
  - `tools` 与 `answers` 是字符串化 JSON
- 当前接入范围故意收窄为：
  - 单轮正例
  - 多工具池可保留
  - 但只接受单个 ground-truth tool call
- 为了兼容真实全量数据，已补一个极窄修复：
  - `xLAM` 的整数型 `id` 现在会被统一转成字符串 `sample_id`
- 当前结果是：
  - `accepted=25711`
  - `rejected=34289`
  - `train=20588`
  - `dev=2553`
  - `test=2570`
- 已新增首批 real-data pilot 配置：
  - `vanilla`
  - `schema_augmented`
  - `hammer_like`
  - 当前统一采用 `1000 steps` 的 `pilot1000` 口径，先做真实数据 bring-up，再决定完整训练预算
- 2026-04-14 当前正在运行的 real-data baseline：
  - `USE_MODELSCOPE_HUB=1 /root/miniconda3/envs/tooluse-llf/bin/llamafactory-cli train configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_vanilla_qlora_pilot1000.yaml`
  - 输出目录：`/root/autodl-fs/tooluse-artifacts/runs/local_2080ti/xlam_fc_single_call/qwen25_05b_vanilla_qlora_pilot1000`
- 相关记录：
  - `docs/records/2026-04-14-xlam-fc60k-ingest-audit.md`

当前新增的协作约束：

- 如果后续推进中确实需要更强的外部方案扩展或纠偏，可以先整理一份高质量 prompt 给用户去问 `GPT-5.4-pro`
- 但这条路径只用于补充判断，不替代本仓库内的实现、实验和文档更新
- 外部检索默认优先看 `2025` 年及以后的资料；如果引用更早材料，优先保留高影响力或官方来源

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

补充说明：

- 当前 `scripts/eval_counterfactual.py` 仍然只是占位聚合器，不代表表 R 已经可跑
- 在真实训练源和 held-out baseline 结果稳定前，不要先写方法结论

## 开源仓库约束

这个仓库要按后续 release 的开源项目维护。

- 不要把 conda 环境放在仓库目录里
- 不要把 editable 第三方源码 checkout 放在仓库目录里
- 不要把 checkpoint、预测文件、loss 图等重产物默认写进仓库目录
- 需要提交可复现实验证据时，统一写进 `results/`，而不是散落在根目录
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
2. 当前这一步已经完成：
   - `xLAM` full-data ingest / paired / export 已经跑通
3. 现在直接进入 real-data baseline 阶段，优先把 `vanilla / schema_augmented / hammer_like` 拆到不同机器上推进。
4. 把 `BFCL` 保持为 benchmark / eval slice，不要先把 benchmark 和训练源混在一起。
5. 继续用 `LLaMA-Factory` 跑 baseline，不要回头扩手写 trainer。
6. 对所有后续预测输出统一跑 exact tool-call evaluator，不再用 BLEU/ROUGE 代替函数调用正确性。
7. 只有真实 held-out baseline 结果成立后，才讨论 `reuse_main` 与表 R 的实现。
