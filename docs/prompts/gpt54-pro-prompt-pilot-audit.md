# GPT-5.4 Pro Prompt: Pilot-V1 Experiment Audit

## 给模型的输入材料

请阅读以下两份文档，并只基于它们开展审查：

- `2026-03-31-nips2026-function-calling-idea-draft-v2.md`
- `2026-04-08-schema-reuse-pilot-v1-implementation-plan.md`

不要自由发散新 research direction，不要重写 thesis，不要引入 RL / EFPD / rerank / framework 作为主线。

## Prompt

你现在扮演一个**非常严格的 NeurIPS reviewer + experiment chair + project survival auditor**。

我要做的是一个 function-calling / tool-use 论文，当前主 thesis 已经被强行收缩为：

- `cross-schema decision reuse`
- 核心主张是：是否存在一个可在等价 schema 间 `encode once, ground many times` 的 decision representation
- 当前主证据链是：`A->B counterfactual decoding + shuffle/null d controls + held-out schema transforms`
- 当前明确**不进入主线**的内容有：`RL`, `EFPD`, `rerank`, `framework`

你要做的不是帮我扩展 idea，而是帮我判断：

**当前这套 pilot-v1 实验设计，是否真的足以支撑或证伪这个 thesis。**

请严格执行下面的约束：

1. 不要把任务改写成别的论文。
2. 不要建议我重新做一个更大的系统。
3. 不要默认“多做实验就行”。
4. 不要把 `RL`、`feedback posterior`、`best-of-n` 拉回主线。
5. 你的工作重点是：找出当前 pilot 是否存在逻辑漏洞、baseline 缺口、混淆因素、不可证伪点。

请输出以下 8 个部分，顺序不要变：

### 1. Executive Verdict

只用 3 种结论之一：

- `PASSABLE`
- `BORDERLINE`
- `NOT YET SCIENTIFICALLY SHARP`

并用 5 句以内说明原因。

### 2. Core Claim Audit

请判断下面 4 个 claim 中，哪些已经被当前 pilot 设计覆盖，哪些没有：

- Claim A: `d` 不是普通压缩码，而是真正参与 grounding 的 reusable decision object
- Claim B: `A->B` 的成功可以被解释为 cross-schema reuse，而不是普通 augmentation gain
- Claim C: 当前的 `G_main` 足够支撑主 thesis，而不会因为变换过弱而失去说服力
- Claim D: 当前 pilot 的失败条件足够严格，不会让项目在坏结果下继续自欺

请对每个 claim 给出：

- `Covered / Partially Covered / Not Covered`
- 1 段理由
- 最关键的 reviewer attack

### 3. Confound Table

请列一个表，至少覆盖下面这些潜在混淆：

- decoder ignores `d`
- `d` 只是 canonical tool id / alignment code
- gain comes from stronger schema augmentation
- gain comes from Hammer-style masking / robustness recipe
- split leakage via transform generation
- alias vocabulary leakage
- evaluation contaminated by `B->B` oracle thinking
- robustness probes 被误当作主证明

对于每个混淆，请给出：

- 为什么危险
- 当前设计是否已经控制
- 如果还没控制，最小需要补什么

### 4. Baseline Audit

请判断当前 baseline 集合是否足够回答下面这几个问题：

- 这是不是 direct SFT + augmentation 就能做到？
- 这是不是 Hammer-style robustness recipe？
- 这是不是 latent head 本身就够了？
- 这是不是 latent consistency 就够了，而 fixed-`d` reuse 不是关键？

请输出：

- `baseline 是否足够`
- 缺的 baseline 是什么
- 哪个 baseline 最可能直接打掉 thesis

注意：

- 只有在你认为**缺失 baseline 会导致主结论不成立**时，才允许新增 baseline
- 不要把 baseline 列表扩展成大而全 benchmark zoo

### 5. Transform Family Audit

当前 `pilot-v1` 只把下面这些放进 `G_main`：

- tool renaming
- argument renaming
- schema key reorder

请你严格判断：

- 这个 `G_main` 会不会太弱，导致即便结果好也不能证明什么？
- 还是说它正好适合作为第一轮主证据？
- `description paraphrase` 和 `argument reshaping` 现在不进主表，是否合理？

请给出结论：

- `too weak / acceptable / too ambitious`

并说明理由。

### 6. Metric and Gate Audit

当前要求主表强制报告：

- `A->A`
- `B->B`
- `A->B`
- `shuffle`
- `null`
- `CF-Gap`

当前内部 gate 主要包括：

- `A->B` 要明显高于 `shuffle/null`
- `CF-Gap` 要优于 matched latent bottleneck
- 要优于 `schema-augmented SFT` 与 `Hammer-style`
- held-out alias 上不能掉光

请判断：

- 这些 gate 是否足够硬
- 是否有关键 gate 缺失
- 哪些 gate 太软或太主观

请给出一个你认可的**最小 gate set**。

### 7. Stop-or-Continue Decision Rule

请给出一个非常明确的决策规则：

- 什么结果出现时，应该 `continue`
- 什么结果出现时，应该 `rewrite as narrower robustness paper`
- 什么结果出现时，应该 `stop this direction`

不要模糊表达，不要说“视情况而定”。

### 8. Minimal Revision List

如果你认为当前文档还不够硬，请只给出**最小修订清单**：

- 最多 5 条
- 每条必须是“补一个具体对照 / 改一个具体规则 / 删一个具体口号”
- 不要给开放式 brainstorming

## 输出风格要求

- 用中文
- 尽量像 reviewer，不要像 coauthor
- findings first
- 不要鼓励，不要安慰
- 不要默认这个项目值得继续，除非证据真的足够
- 如果你认为当前设计仍然不够支持 thesis，请直接说

## 最后一句强制要求

你的最终目标不是帮我把这个方向说圆，而是帮我判断：

**如果按当前 pilot-v1 做下去，出来的结果到底能不能支撑一篇严肃的 NeurIPS function-calling 方法论文。**
