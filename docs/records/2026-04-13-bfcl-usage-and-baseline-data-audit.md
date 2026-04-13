# 2026-04-13 BFCL 用法与 baseline 数据源审计

## 背景

今天本机已经把官方 `BFCL v4` 的一部分单轮单工具数据接进来了，并成功构建了：

- `data/interim/bfcl_v4_single_turn/candidates.jsonl`
- `data/processed/bfcl_v4_single_turn/{train,dev,test}.jsonl`
- `data/llamafactory/bfcl_v4_single_turn/*`

accepted 结果：

- 总 accepted：`774`
- split：
  - `train=609`
  - `dev=94`
  - `test=71`

但在继续把它当成 baseline 训练集之前，先查了一轮外部论文和工程，确认社区通常如何使用 `BFCL`，以及更常见的 baseline 训练数据源是什么。

## 外部实践结论

### 1. BFCL 官方定位首先是 benchmark / evaluation

官方 `BFCL` README 和 Hugging Face 数据页都把它描述成 function-calling evaluation 数据与评测框架；官方评测依赖 `possible_answer` 中的可接受答案集合，而不是单一 canonical target。

这意味着：

- 把 `possible_answer` 直接压成一个唯一监督答案会丢失 benchmark 原始语义；
- 如果直接用 `BFCL` 当训练主料，需要额外论证为什么这样做不会扭曲 benchmark 定义。

## 2. 主流 function-calling 训练工作更常见的做法：训练用自建/合成数据，BFCL 用来评测

### APIGen / xLAM

`APIGen` 明确发布了 `60,000` 条“可验证、高质量”的 function-calling 训练数据，并报告“在这些数据上训练后，再去 BFCL 上评测”。

这类做法和我们的 baseline 需求更一致：

- 训练集本身就是为 supervised function calling 设计的；
- 数据里已有明确工具定义与目标调用；
- benchmark 与训练源分离更干净。

### Hammer

`Hammer` 官方仓库写得很直接：

- 训练数据：`Salesforce/xlam-function-calling-60k` + 自己的 irrelevance 数据；
- 评测：`BFCL`、`API-Bank`、`Tool-Alpaca`、`NexusRaven`、`Seal-Tools`。

这进一步说明，至少在较新的开源工程里，`BFCL` 更常被当 benchmark，而不是主训练源。

### When2Call

`When2Call` 官方仓库同样把：

- `BFCL` 用于生成 evaluation data；
- `xlam-function-calling-60k` 用于生成 train data。

这和我们的当前问题高度相关，因为 `When2Call` 本身就在处理“什么时候该调 / 不该调工具”的 decision 问题。

### Granite Function Calling

IBM Granite 的 function-calling 论文使用的是多任务训练数据混合：

- `API-Blend`
- `Glaive-V2`

然后在 `BFCL` 和其它 benchmark 上做泛化评测。

它同样没有把 `BFCL` 当主训练集来讲。

## 当前判断

目前更稳的定位应该是：

- `BFCL`：
  - 作为官方 benchmark ingest / audit / evaluation 路径；
  - 可以构建 repo 内部的 clean eval slice；
  - **暂时不要**直接升级成 baseline 默认训练源。
- baseline 训练数据源：
  - 应优先从社区常见的 function-calling training datasets 中选择。

## 候选 baseline 数据源排序

### 第一优先级：`Salesforce/xlam-function-calling-60k`

原因：

- 官方 APIGen 产物；
- 明确是训练数据；
- 带 verifiable 叙事；
- 已被多个开源项目和模型卡实际采用；
- 和我们现在的单轮 function-calling baseline 最契合。

### 第二优先级：`Team-ACE/ToolACE`

原因：

- 官方 ToolACE 数据集；
- 规模约 `11.3k`；
- 更偏复杂、agentic、multi-turn / tool-use conversation；
- 适合作为更难的数据源或后续增强集，但未必是最先接的 baseline 主料。

### 第三优先级：`When2Call` / irrelevance 数据

原因：

- 如果后面要补 `null / irrelevance / should-not-call` 控制组，这类数据非常有价值；
- 但它更像 baseline 的补充维度，不是最先替代 `pilot_v1` 的主正例训练集。

### 第四优先级：`APIGen-MT-5k`

原因：

- 明确面向 multi-turn function-calling；
- 如果论文后面真的扩到 multi-turn，再接更合理；
- 当前主线仍是单轮 schema reuse，不宜过早引入。

### 次优先选择：`glaive-function-calling-v2`

原因：

- 社区使用广；
- Granite 训练混合里也用了它；
- 但其公开说明对数据生成过程不够透明，适合当补充混合源，不建议先单独作为核心 baseline 训练源。

## 对当前仓库的直接影响

今天新增的 `bfcl_v4_single_turn` 路径保留，但定位要改成：

- `benchmark ingest`
- `clean eval slice`
- `格式与评测链路验证`

而不是：

- “已经确认的 baseline 训练主料”

## 建议的下一步

1. 先检查 `Salesforce/xlam-function-calling-60k` 的字段格式与 license。
2. 确认它是否能无损映射到当前 repo 的：
   - `user`
   - `tool schema`
   - `ground truth call`
   - `single-turn` paired-schema transform
3. 如果可以，优先把 `xLAM/APIGen` 接成 baseline 训练源。
4. 保留 `BFCL` 路径作为 held-out eval / audit，不要先把 benchmark 和训练源混在一起。

## 参考来源

- BFCL 官方仓库：
  - `https://github.com/ShishirPatil/gorilla/tree/main/berkeley-function-call-leaderboard`
- BFCL Hugging Face 数据页：
  - `https://huggingface.co/datasets/gorilla-llm/Berkeley-Function-Calling-Leaderboard`
- APIGen 论文：
  - `https://arxiv.org/abs/2406.18518`
- xLAM 官方仓库：
  - `https://github.com/SalesforceAIResearch/xLAM`
- xLAM 训练数据：
  - `https://huggingface.co/datasets/Salesforce/xlam-function-calling-60k`
- Hammer 官方仓库：
  - `https://github.com/MadeAgents/Hammer`
- When2Call 官方仓库：
  - `https://github.com/NVIDIA/When2Call`
- Granite Function Calling 论文：
  - `https://aclanthology.org/2024.emnlp-industry.85/`
- ToolACE 论文：
  - `https://arxiv.org/abs/2409.00920`
