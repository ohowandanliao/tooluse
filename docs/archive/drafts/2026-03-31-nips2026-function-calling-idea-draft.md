# NeurIPS 2026 Function Calling Idea Draft

## 1. 目标

这份文档用于后续 deep research，不是最终论文写作稿。目标是把当前最推荐的方向、方法定义、实验计划、主要风险和退出条件压缩成一份更干净的输入文档。

核心约束：

- 主题必须仍然是 `function calling / tool use`
- 不做大而全的 agent 框架
- 可以接受少量 RL，但需要显式比较 `no-RL` 与 `+RL`；RL 是否构成必要条件由实验决定
- 需要有明确的方法贡献，也需要有能证明方法不是“换皮 recipe”的实验协议

## 2. 最终判断

当前最推荐的收敛方式是：

**A 作为方法，B 作为证据链，C 作为可选扩展。**

对应到更具体的表述：

- **A：Latent Posterior Refinement for Function Calling**
  作为主方法线
- **B：Schema-Invariant Evaluation Protocol**
  作为主实验协议和关键证据链
- **C：Multi-Candidate Latent Policy with Executability Re-ranking**
  只保留为误差分析驱动的扩展，不作为当前主线

一句话总结：

**项目主线应当是“schema-abstracted decision representation + execution-feedback posterior distillation”，而不是“CoLA + function calling adaptation”。**

## 3. 为什么推荐这条线

### 3.1 不推荐直接做 CoLA for function calling

直接顺着 CoLA 往下做，最大的问题是论文会被理解成：

- action-space compression 的应用化改造
- latent action 在 tool use 场景下的迁移

而不是一个新的 function calling 问题定义。

更具体地说，CoLA 给了一个重要起点：`s -> z`，即从 token action 到 latent action 的抽象。但它没有解决三件更关键的事：

- `z` 是否真的对齐到 tool-use decision，而不是压缩码
- `z` 如何和具体 tool schema 解耦
- 执行后的 feedback 如何真正作用在 decision 层，而不是仅作用在 surface token 层

如果论文只做到“CoLA 改一下用在 function calling”，亮点不够硬。

### 3.2 为什么 A 值得做

A 方向真正有新意的地方不在于“我们也用了 latent action”，而在于：

- 把 function calling 的学习对象从 `tool-call token` 改成 `latent decision`
- 把执行后反馈的更新对象从 `output token` 改成 `latent decision posterior`
- 把 schema / tool variation 当成一等公民目标，而不是附属 stress test
- 把 `decision invariant / grounding equivariant` 当成方法结构，而不是事后解释

这条线更像一个完整的方法主张：

**execution feedback should refine latent decisions rather than surface tool-call tokens**

### 3.3 为什么 B 必须存在

B 不只是第二亮点，它其实是 A 成立的关键证据链。

如果没有一套系统的 schema / tool variation stress test，我们很难证明：

- latent 真的学到了比 tool identity 更稳定的决策对象
- posterior refinement 真的比 token-level hindsight 更能迁移
- gain 不是来自更强 augmentation 或更强 prompt engineering

所以 B 的角色应该是：

- 不是第二条独立方法
- 而是 A 的主实验协议

### 3.4 为什么 C 暂时不该作为主线

C 方向看起来很自然，但目前研究价值被高估了。

原因有三点：

- BFCL 风格任务未必天然强多模态，很多例子更接近近确定调用
- 很容易退化成 `best-of-n + rerank` 或 verifier 增强
- 如果进一步引入 diffusion / flow，工程复杂度会上升，但方法主张不一定变强

因此当前更稳的判断是：

- C 可以保留
- 但只适合在 A 已经成立后，再用误差分析决定要不要做

## 4. 推荐的论文命题

最推荐的标题方向是：

- **Schema-Invariant Decision Distillation for Executable Function Calling**
- **Execution-Feedback Distillation in a Schema-Abstracted Decision Space**
- **From Tokens to Decisions: Posterior Distillation for Robust Tool Calling**

对应的核心命题是：

> Function calling should be learned in a latent decision space, and execution feedback should refine latent decisions rather than surface tool-call tokens.

这个命题包含三个可以被检验的子主张：

1. function calling 的正确建模对象应当是 latent decision，而不是 tool-call token
2. hindsight feedback 更适合用于 refinement `p(d | s, T)`，而不是 repair `p(y | s, T)`
3. 一个好的 decision representation 应该对 schema 变换近似不变，而 grounding 对 schema 变换应当等变

## 4.1 这篇论文到底解决什么问题

这篇论文如果成立，解决的是下面这个具体问题：

**现有 function calling 方法大多直接学习 schema-bound 的 tool-call tokens，因此在 tool renaming、argument renaming、format variation、irrelevant tools、enlarged tool pools 等设置下会发生系统性退化；同时，执行后反馈大多被用于 token repair，而不是 decision update。**

更细一点说，这篇论文试图同时解决两个相互耦合的问题：

- **决策对象错了**：模型学的是工具名、参数键、格式模板，而不是可跨 schema 复用的 decision representation
- **反馈作用点错了**：执行后反馈主要被用于修 token 输出，而不是修“本来该做什么”的 decision posterior

所以这篇论文不是在解决“怎么把 JSON 生成得更漂亮”，而是在解决：

- function calling 是否应该首先学习一个 schema-abstracted decision representation
- execution feedback 是否应该首先更新这个 decision representation

## 4.2 打算怎么解决

最小闭环就是三件事：

1. **先学 decision，不直接学 tool token**
   用 `p(d_t | s_t, T_t)` 先产生 decision representation

2. **再做 schema-conditioned grounding**
   用 `p(y_t | d_t, s_t, T_t)` 把 decision representation 映射到当前 schema 下的可执行 tool call

3. **用 execution feedback 蒸馏更好的 posterior**
   从 `f_t` 构造 `q(d_t | s_t, f_t)`，再让 prior 去逼近 posterior

这条线的关键不是“加了多少模块”，而是：

- 把 learning target 从 `y` 换成了 `d`
- 把 feedback update target 从 `y` 换成了 `d`
- 把 schema variation 从 stress test 变成了主训练/主评测约束

## 4.3 相对其他文章的新意到底在哪

这部分必须写得很克制，否则很容易被 reviewer 打成拼接工作。

### 相对 CoLA

CoLA 的核心是 latent action space abstraction，本质上解决的是动作空间结构和探索效率问题。

这篇工作如果成立，真正多出来的是：

- CoLA 没有把 schema variation 写成目标结构
- CoLA 没有把 execution feedback 的主要作用点放在 decision posterior
- CoLA 没有回答“同一个 decision 是否能跨 schema 复用”

所以相对 CoLA 的新意不应写成“我们也用了 latent”，而应写成：

- `decision invariant / grounding equivariant`
- `execution-feedback posterior distillation`
- `counterfactual decision reuse`

### 相对 SDPO / OpenClaw-RL

SDPO / OpenClaw 解决的是 rich feedback 如何变成 dense learning signal，但主要对象仍然是 token prediction。

这篇工作的真实增量应当是：

- 同样使用 feedback，但更新对象是 `decision posterior`
- 不是比较“谁更会修 token”，而是比较“谁在跨 schema 时更稳”
- 用同一 feedback budget 的 apples-to-apples 实验，证明 decision-level update 比 token-level update 更可迁移

### 相对 Hammer

Hammer 解决的是 naming overfit 和 irrelevant-function sensitivity，主要方法是 masking 和数据增强。

这篇工作的真实增量不应写成“更强鲁棒性技巧”，而应写成：

- 命名鲁棒性不再只是 augmentation 目标
- 而是被吸收到 decision/grounding 分离的结构里
- 并且通过 counterfactual reuse 去证明不是简单 prompt / masking recipe

## 4.4 亮点够不够 2-3 个

如果实验成立，这篇论文的亮点是够的，而且应该只保留 3 个，不要再扩。

### 亮点 1：新的问题结构

把 function calling 写成 `decision invariant / grounding equivariant` 的两层结构，而不是直接学 schema-bound tool-call tokens。

### 亮点 2：新的 feedback 注入位置

把 execution feedback 的主要作用点从 token repair 改成 decision posterior distillation，并与 token-level hindsight 做同 budget 对照。

但这一点当前必须按**受限版本**来表述：

- 只有在严格对齐 feedback budget 后仍然成立，才能写成主贡献
- 如果 fairness audit 后发现主要收益来自额外可见信息，这一点就只能降为次级观察，而不能写成核心 novelty

### 亮点 3：新的证据链

用 schema perturbation + counterfactual decoding 证明模型学到的是可复用 decision，而不是压缩码或 recipe engineering。

这 3 个点已经够了。再额外加：

- affordance-heavy 模块
- 重型 RL
- multi-candidate rerank
- diffusion / flow

只会稀释主线。

## 5. 推荐的方法定义

## 5.1 基本形式化

把单步 function calling 写成两层：

- 高层决策：`p(d_t | s_t, T_t)`
- 低层 grounding：`p(y_t | d_t, s_t, T_t)`

其中：

- `s_t`：当前状态，包含用户请求、对话历史、已有工具返回、当前可用工具集合
- `d_t`：decision representation，表示当前步的语义动作 / tool-use intent
- `y_t`：最终生成的可执行 tool call
- `T_t`：当前工具集合或 schema 集合

关键点：

- 真正被优化的对象是 `d_t`
- `y_t` 是 `d_t` 在当前工具集合下的 realization

这里需要把 schema 变换集合 `G` 定义清楚。当前建议只承认以下几类等价变换：

- tool renaming
- argument renaming
- doc / description paraphrase
- 少量可逆的 argument reshaping

硬约束：

- 每个 `g ∈ G` 必须可构造双射映射（bijection）
- ground-truth call 必须能被同一个 `g` 映射到目标 schema
- 如果用户文本里显式出现 tool / parameter 名称，需要过滤这类样本，或对用户文本做一致替换并单独说明

对这些变换 `g ∈ G`，目标不是让输出 token 不变，而是：

- **decision invariant**：`p(d_t | s_t, T_t) ≈ p(d_t | s_t, g(T_t))`
- **grounding equivariant**：在 `g(T_t)` 下对 `d_t` 的 decoding 应产生语义上对应的调用

这层结构必须写实，否则论文会被理解成“CoLA 迁移 + consistency regularization”。

## 5.2 方法骨架

建议做成一个轻量三段式，而不是完整 CoLA 复现：

### 模块 1：Decision Encoder

输入：`s_t`

输出：离散 latent code 或低维 decision state `d_t`

最小实现建议：

- 一个分类头输出离散 `d_t`
- codebook 大小先试 `K = 32 / 64 / 128`
- 不追求复杂 latent dynamics

### 模块 2：Grounding Decoder

输入：`d_t + s_t + T_t`

输出：tool name + arguments

目标：

- 把 decision representation 映射成当前 schema 下可执行的 function call
- 这里要尽量简单，避免演变成另一个大系统

可接受实现：

- constrained decoder
- schema-aware decoder
- tool compiler 风格模块

### 模块 3：Hindsight Posterior Module

执行 `y_t` 后得到 `s_{t+1}`

构造一个 feedback-conditioned posterior：

- `q(d_t | s_t, f_t)`

这里 `f_t` 不应无约束地等于完整 `s_{t+1}`。为了避免 teacher leakage，建议分层限制 posterior 可见的反馈预算：

- Level A：executable / non-executable flag + coarse error type
- Level B：Level A + 压缩后的 tool result summary
- Level C：Level B + 用户纠正

主实验里，decision-level posterior 与 token-level hindsight baseline 必须使用相同 feedback budget，避免“teacher 看得更多所以更强”。

但经过 Prompt 2 的审查后，需要进一步收紧：

- 这里只是 **feedback budget**，不是完整的 same-budget 定义
- Level A 更适合作为主表中的最严格版本
- Level B 只有在 summary 规则固定、且 token baseline 接收完全同构的信息时，才适合作为主表
- Level C 泄漏风险最高，更适合作为 auxiliary setting，而不应默认作为主 claim 证据

换句话说，Claim 2 的主表不能只说“feedback budget 一样”，而必须说明还有哪些预算也被对齐了。

这一步是整篇工作的核心。

## 5.3 训练目标

建议只保留三个主要训练信号，不要做复杂拼盘。

### Loss 1：Grounding Loss

作用：

- 让模型学会把 `d_t` grounding 成正确 tool call

可以是标准的 tool-call generation loss。

### Loss 2：Posterior Matching Loss

作用：

- 让 `p(d_t | s_t, T_t)` 去逼近 `q(d_t | s_t, f_t)`

可以先用最简单的形式：

- cross-entropy
- 或 `KL(q || p)`

这是最关键的 loss。

### Loss 3：Schema Consistency Loss

作用：

- 让同一语义任务在等价 schema 扰动下得到更稳定的 decision representation

最自然的两种做法：

- consistency regularization
- contrastive objective

这部分不一定要很重，但非常重要，因为它直接支撑论文的 schema-invariant 主张。

### 训练 / 评测协议：Counterfactual Decoding

这不是额外模块，而是必须存在的核心协议。

做法：

- 对每个样本，从等价变换族 `G` 中随机采样 `g_ω`
- 构造 `(T_A, T_B = g_ω(T_A))` 及其对应的 ground-truth 映射
- 先在 schema A 下编码得到 `d_A = E(s, T_A)`
- 不重新编码 `d_A`
- **仅替换 schema 输入为 `T_B`，不允许替换 grounding head**
- 做 counterfactual decoding：`y_{A→B} = D(d_A, s, T_B)`
- 再做正常 B 侧编码：`y_{B→B} = D(E(s, T_B), s, T_B)`

如果这一步做不到，`decision / grounding` 分离的主张就是假的，`d_t` 很可能只是压缩码。

主指标建议直接写成：

- `CF-ExecAcc / CF-ASTAcc`
- `CF-Gap = Acc(y_{B→B}) - Acc(y_{A→B})`

同时必须加入两个 `d`-介入对照，否则 reviewer 会质疑 decoder 根本没在用 decision：

- `shuffle control`：batch 内随机置换 `d_A`
- `null control`：把 `d_A` 替换成固定空值 / 最常见 code

要求：

- `y_{A→B}` 明显优于 shuffle / null
- `CF-Gap` 足够小，说明不重编码的跨 schema grounding 损失受控

补充说明：

- `counterfactual decoding` 是主张 1 和主张 3 的核心证据
- 若要让主张 2 也被它覆盖，需要再做一个 **带 feedback 的 counterfactual 版本**：先在 A 下产生反馈，再比较 decision-posterior 与 token-hindsight 在同 feedback budget 下的跨 schema reuse

### Optional：Light RL Calibration

RL 不应被预设为“必要”或“可忽略”，而应被当作一个需要显式验证的二阶段优化器。

当前更合理的立场是：

- formulation 上，主 thesis 应该能在 `no-RL` 版本下被检验
- empirical 上，必须报告 `A-noRL` 与 `A+RL`
- paper positioning 上，是否把 RL 写成必要组成部分，应由实验决定

也就是说，不是先决定“依赖 RL”还是“不依赖 RL”，而是让实验来回答：

- 核心收益是否在 `no-RL` 下已经成立
- RL 是否只是进一步增强
- 还是说没有 RL 根本立不住主 thesis

建议 reward 足够简单：

- executable success
- end-task success
- error recovery bonus
- tool cost penalty

建议只更新：

- latent head
- 少量 adapter / LoRA
- optional grounding head

不要把 RL 预先写成整篇工作的主要 novelty 来源。更稳的默认策略是：

- 主稿的核心 thesis 先按 `no-RL` 能否成立来设计
- RL 作为明确评估的一条增强分支保留
- 最终论文是否“依赖 RL”，由结果决定

## 5.4 训练流程

建议按三阶段做：

### Stage 1：Base SFT

目标：

- 先学会标准 function calling

训练数据来源：

- 公开 tool-use / function-calling 数据
- 自合成 BFCL-style 数据
- 其他可执行 tool-call 轨迹数据

注意：

- BFCL 更像评测，不建议直接作为主训练源
- 即便作为评测，BFCL-v3 多轮部分也应做 sanity check 或 audit-aware 子集过滤

### Stage 2：Hindsight Posterior Refinement

目标：

- 用执行后反馈修正 decision representation

做法：

- rollout 一批工具轨迹
- 收集 `s_t, y_t, s_{t+1}`
- 构造 feedback-conditioned teacher / posterior
- 在与 token-hindsight 相同 feedback budget 下 distill 回 `p(d | s, T)`

### Stage 3：Light RL Calibration（可选）

目标：

- 校准 success / efficiency / recovery

要求：

- 必须同时保留 `A-noRL` 和 `A+RL`
- 不能只报告加 RL 后的版本
- 如果只有 `A+RL` 才成立，论文叙事就要相应改写，并更认真对比 ToolRL / TRM / reward-model 路线

## 6. 论文贡献点应该怎么写

最推荐的 3 个贡献点是：

### 贡献点 1：Decision-space modeling with schema structure

把 function calling 从 tool-token prediction 改写成 `decision invariant / grounding equivariant` 的两层结构。

### 贡献点 2：Execution-feedback posterior distillation

执行后反馈不再修 surface token，而是修 decision posterior，并且与 token-level hindsight 在相同 feedback budget 下做对照。

当前更稳的写法是：

- 先把它当作**待严格审查的主贡献候选**
- 只有在 same-budget 公平对照和必要的 feedback-conditioned counterfactual 证据都成立后，才升格为正式主贡献

### 贡献点 3：Counterfactual decision reuse under schema variation

通过系统的 schema variation stress test 与 counterfactual decoding，证明模型学到的不是简单压缩码。

这三个贡献点加起来已经足够构成一篇方法论文。前提是：

- 贡献点 1 不能被归因为 CoLA adaptation
- 贡献点 2 不能被归因为 SDPO / OPD 换空间
- 贡献点 3 必须有硬实验支撑，而不是只靠自定义 latent 指标

## 7. 实验计划

## 7.1 总体策略

实验设计的目标不是“尽量全”，而是“尽快判断主张是否站得住”。

所以顺序应该是：

1. **先做 go / no-go 小实验**
2. **再做主 benchmark**
3. **最后做外部 robustness 验证和可选扩展**

## 7.2 Go / No-Go Pilot

这是最重要的一组实验。

目的：

- 判断 A 是否真的比 token-level hindsight 更有意义
- 判断 latent 是否真的在 schema variation 下更稳定
- 判断 C 是否暂时可以直接放弃

### 数据

- 经过 sanity check 的 BFCL-v3 小子集
- 自建小规模 schema perturbation set

### 对比方法

- Vanilla SFT
- Hammer-style schema masking
- CoLA-lite without posterior refinement
- token-level hindsight baseline
- A-mini：latent decision + posterior refinement
- A-mini + RL
- optional：token-hindsight + RL

### 最关键的观测

- normal setting 下是否有收益
- schema perturbation 下是否更稳
- counterfactual decoding 是否成立
- token-level hindsight 是否已经吃掉主要收益
- `A-noRL` 和 `A+RL` 的关系是什么

### Go / No-Go 标准

如果出现下面任一情况，A 方向需要大改甚至暂停：

- 只在 normal BFCL 上有小幅提升，但在 schema perturbation 下无明显优势
- counterfactual decoding 基本不成立
- token-level hindsight baseline 已经覆盖主要收益
- 改进主要来自参数修复，而不是跨 schema 迁移或错误恢复
- 只有 `A+RL` 有效，而 `A-noRL` 基本不成立，且同预算 token-hindsight + RL 也接近

## 7.3 主实验

如果 pilot 支持 A，再做主实验。

### 主 benchmark

- BFCL-v3 multi-turn
- BFCL-v4 中和 prompt variation / format sensitivity 更相关的设置

注意：

- BFCL-v3 多轮部分有已知审计风险，主实验应明确是否使用经过人工复核或 audit-aware 过滤的子集
- BFCL 用作主评测，不用作主训练源

### 核心 stress tests

必须做的 schema / tool variation：

- tool renaming
- argument renaming
- irrelevant tools injection
- enlarged tool pool
- description paraphrase
- limited reversible argument reshaping

可选：

- unseen tool family
- execution noise

### 外部验证

- WILDAGTEVAL 小规模子集

定位：

- 不作为主战场
- 只作为 robustness probe

## 7.4 Same-Budget Protocol

Prompt 2 最重要的修正是：

**same-budget 不等于只对齐 feedback budget。**

如果要让 Claim 2 可辩护，主对照至少需要同时报告下面几类预算：

- **model budget**：相同 base model；若使用 adapter / latent head，需让 token baseline 也拥有同量级可训练容量，或至少单独报告新增参数量
- **data budget**：相同 SFT 数据量、相同 hindsight / feedback 样本数、相同 schema-perturbation 暴露范围
- **feedback budget**：相同反馈通道、相同压缩规则、相同可见字段；不能让 posterior teacher 看到 token baseline 看不到的结果字段
- **environment budget**：相同工具执行次数、相同 judge / verifier / evaluator 调用次数、相同 RL rollout 次数
- **optimization budget**：相同更新步数或近似训练 FLOPs；若做 `+RL`，则 `A+RL` 必须与 `token-hindsight+RL` 匹配
- **inference budget**：相同最大解码长度、相同 repair 次数、相同候选数；不能让某一路径通过更多 retry 获得隐性优势

更稳的写法是：

- 主文只把 `same-budget` 用在上述多维预算都对齐，或至少都被完整报告的实验上
- 如果某些预算无法完全对齐，就把它降级为 auxiliary evidence，而不要让它承载主 claim

## 7.5 Baselines

最少需要覆盖：

- Vanilla SFT function-calling baseline
- Hammer-style schema masking baseline
- CoLA-lite / CoLA-adapted baseline
- token-level hindsight baseline，例如 OpenClaw / SDPO-lite
- standard distillation baseline
- scratch-matched fine-tuning baseline
- A-noRL
- A+RL
- optional：token-hindsight + RL
- optional：ToolRL-lite 或 TRM-lite

第二优先级可选 baseline：

- semantic tool encoding baseline
- hierarchical tool encoding baseline

但它们不应该挤占与 Hammer / token-hindsight / CoLA-lite 的主对照预算。

对 Prompt 2 里提到的其他 baseline，当前判断是：

- `token-hindsight + RL` 如果最终主表保留 `A+RL`，就应尽量升级为必做
- `RLHF` 不应进入主矩阵，除非最后论文真的被改写成 RL-dependent thesis
- `CoT prompting` 最多作为 appendix sanity check；它改变的是 inference prompt，而不是训练对象，不应挤占主线预算

## 7.6 指标

建议把指标分成四类。

### A. 基础性能

- executable accuracy
- function-call success
- end-task success

### B. 迁移与鲁棒性

- schema perturbation gap
- unseen-tool transfer
- enlarged-tool-pool robustness

### C. 过程表现

- error recovery rate
- tool-call efficiency
- latency / extra compute
- reported budget ledger

### D. Latent 诊断

- counterfactual decoding score
- same-task cross-schema alignment
- inter-task separability

第四类非常重要，因为它直接关系到“decision representation 是否只是压缩码”。其中 `counterfactual decoding score` 应该是主图，而不是附属诊断。

补充要求：

- 关键主表必须同时报告预算账本，而不是只报性能点值
- 至少报告：新增参数量、训练步数或近似 FLOPs、反馈调用次数、环境交互次数、是否使用 RL

## 7.7 统计可靠性

Prompt 2 另一个有效提醒是：

**这篇论文如果要主打 Claim 2，不能只给单次跑出来的点值。**

更现实的要求是：

- pilot 阶段关键对比至少做 `3` 个随机种子
- 最终主表关键结论优先做 `5` 个随机种子；若 `+RL` 成本过高，至少 `3` 个并明确说明
- 报告 mean ± standard error 或 95% CI，而不是只报 best run
- 只对最关键比较做显著性检验，避免把实验预算耗在低价值比较上

最关键的统计对比应该是：

- `A-noRL` vs token-hindsight
- `A+RL` vs token-hindsight + RL
- counterfactual decoding 下的 `A→B` vs controls

此外必须保证：

- BFCL 审计子集与任何训练 / 蒸馏样本严格隔离
- schema perturbation test 中的变换族和样本切分不与训练泄漏

## 7.8 Ablations

必须做的消融：

- 去掉 posterior refinement，只保留 latent head
- 用 token-level hindsight 替换 latent posterior
- 去掉 schema consistency loss
- 去掉 grounding 解耦，直接从 latent 解码 tool token
- 去掉 RL calibration
- 只保留 +RL 版本，不保留 no-RL 版本
- 限制 posterior feedback budget
- 去掉 schema-shared decision reuse 设定，只允许每个 schema 独立编码

这些消融的目标不是凑表，而是回答最关键的审稿质疑：

- 这是不是只是 CoLA 的工程变体
- 这是不是只是 OPD / SDPO 换了个空间
- 这是不是只是更强 augmentation

## 8. 对三个方向的最终处置

## 8.1 A：主方法，继续推进

继续推进的前提是：

- pilot 能证明 schema robustness 确实提升
- counterfactual decoding / cross-schema reuse 能提供额外证据
- token-level hindsight 没有已经覆盖主要收益
- 至少存在一种合理设定使 `A-noRL` 已经有可辩护的收益；否则需要把论文改写成 RL-dependent thesis

## 8.2 B：保留，但作为实验协议和轻量约束

B 不应该再被理解成独立论文方向。

更合适的定位是：

- A 的关键实验协议
- A 的一个轻量辅助模块

比如：

- schema-invariant consistency regularization
- schema perturbation protocol
- counterfactual decoding protocol

## 8.3 C：暂时降级

只有在下面条件都满足时，C 才值得重新捞起来：

- 误差分析显示失败主要来自多策略选择
- simple reranking / best-of-n 还没有吃掉主要收益
- 额外 compute 成本可接受

否则，C 暂时不要投入主力。

## 9. 目前最主要的风险

### 风险 1：latent 仍然只是压缩码

这是最大的研究风险。

应对方式不是写更多 related work，而是做更硬的实验：

- counterfactual decoding
- posterior vs token-hindsight 对比
- 去掉 posterior 后的退化实验

### 风险 2：posterior teacher leakage

如果 posterior 看到了 token baseline 看不到的信息，收益就可能来自额外监督而不是学习对象改变。

应对原则：

- 明确分层 feedback budget
- token-hindsight 与 decision-posterior 使用相同反馈预算
- 主表里至少报告一个最严格的受限反馈版本
- 在 fairness audit 完成之前，不应把 claim 2 写成“已经被证明成立”，而应写成“需要通过同预算对照来验证”

### 风险 3：项目重新膨胀成框架工作

最容易膨胀的地方：

- 复杂 latent world model
- 大型 affordance ontology
- 重型 RL
- 多候选 diffusion / flow policy

原则：

- 每个模块都只保留最小必要形态

### 风险 4：BFCL 被误用为训练主源或受评测噪声影响

BFCL 更适合作为 held-out benchmark。

如果直接大量吃进训练，容易削弱论文的说服力。即便只做评测，也要处理 BFCL-v3 多轮条目的审计风险。

### 风险 5：RL 归因错误

如果最终结果显示主要收益只在 `+RL` 条件下出现，而 no-RL 版本立不住，那么论文主张就不能再写成“新的学习对象本身成立”，而必须改写成“该 decision-space principle 更适合和 RL 结合”。

## 10. Kill Criteria

以下任一成立，就应当暂停或重写主线：

- token-level hindsight baseline 在 renaming / enlarged tool pool 下与本方法持平或更好
- counterfactual decoding 基本不成立
- 去掉 schema consistency 后，鲁棒性几乎不变
- 关键增益在经过 BFCL-v3 审计子集复核后消失
- 只有 normal BFCL 提升，schema perturbation 下优势消失
- `A-noRL` 无法成立，且 `A+RL` 的增益可被 token-hindsight + RL 解释

## 11. 明确不建议做的事

下面这些方向目前都不建议优先做：

- 完整复现 CoLA 叙事
- 把 diffusion / flow 当主卖点
- 一开始就做复杂 open-world API environment
- 一开始就做 full agent framework
- 把 C 当主线

## 12. 当前最值得坚持的一句话

如果只保留一句话作为后续 deep research 的起点，那就是：

**本项目最值得押的方向是：在 function calling 中学习对 schema 变换近似不变的 decision representation，并让 execution feedback 去蒸馏 decision posterior，而不是修正 surface tool-call tokens。**

## 13. 参考入口

- CoLA: https://proceedings.mlr.press/v267/jia25e.html
- What Do Latent Action Models Actually Learn?: https://openreview.net/pdf?id=DQMjemrVhe
- OpenClaw-RL: https://arxiv.org/html/2603.10165v1
- SDPO: https://arxiv.org/abs/2601.20802
- Hammer: https://iclr.cc/virtual/2025/poster/27722
- BFCL v3: https://gorilla.cs.berkeley.edu/blogs/13_bfcl_v3_multi_turn.html
- BFCL v4: https://gorilla.cs.berkeley.edu/blogs/15_bfcl_v4_web_search.html
- BFCL v4 format sensitivity: https://gorilla.cs.berkeley.edu/blogs/17_bfcl_v4_prompt_variation.html
- BFCL-v3 audit / repair: https://arxiv.org/html/2603.05553v1
- ToolRL: https://arxiv.org/html/2504.13958v1
- TRM: https://openreview.net/forum?id=LnBEASInVr
- WILDAGTEVAL: https://arxiv.org/pdf/2601.00268
- ToolWeaver: https://arxiv.org/abs/2601.21947
- Toolscaler: https://aclanthology.org/2025.findings-emnlp.30/
