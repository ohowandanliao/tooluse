# Tool Function Bottleneck Analysis

- Share URL: https://chatgpt.com/share/69df6227-fe64-8322-9923-f95eb9cec5a4
- Source title: Tool Function Bottleneck Analysis
- Note: inline ChatGPT share citations were normalized to `[Ref n]`. Reference links below were reconstructed from the same share-page payload; some groups may still be partial.

## Result

## 我的明确判断

先别把这件事做成“agent RL / multi-turn 大工程”。第一篇最强的论文，应该是一个 **single-turn、语义固定、工具池可控的 causal measurement paper**：把 function-calling 失败干净拆成你定义的三类瓶颈，再判断 **interface-grounding 是否在 clean regime 下已经是 first-order bottleneck**。

原因很直接。2025+ 的证据已经显示三类问题都真实存在，但没人把它们系统拆开：When2Call 指向 decision；Hammer、BFCL V4 的 format-sensitivity、IFEval-FC、MLCL 都指向 interface-grounding；toolkit expansion、Meta-Tool、MCPVerse、CONFETTI 又明确显示大工具池和近邻工具会引入独立的 search/calibration 失败。现在缺的不是“再做一个更强 agent”，而是 **一篇把 bottleneck attribution 做对的论文**。[Ref 1]

同时，multi-turn benchmark 已经把 scientific object 扩大了。BFCL 自己就说 single-turn 上 SOTA 已经强，但 memory、dynamic decision-making、long-horizon reasoning 仍是 open challenges；ToolSandbox 强调 state dependency / insufficient information；BFCL v4 memory 明确在测 memory tools；τ²-bench 显式分 reasoning vs communication/coordination；WildToolBench 则把 implicit intent spread、instruction transition、compositionality 作为主难点，并报告极低 session accuracy。那不是“更纯的 interface 测试”，而是 memory、state tracking、coordination、planning 乃至 user-simulator fidelity 一起进来了。[Ref 2]

还要压一下你的直觉：接口不是任何任务里都自动 first-order。DBGorilla 的数据库查询实验里，structured generation、one-tool-per-collection、parallel calling 对结果影响都不大；一个 2026 的 schema-first 控制实验也只看到 schema 降低 interface misuse，但没有提升 end-task success，semantic misuse 仍主导。也就是说，你现在最该做的不是“相信 interface 很重要”，而是 **证明它在什么 regime 下是 first-order**。[Ref 3]

---

## 1) 可投稿的问题定义：我建议你这样 formalize

先给统一记号。对每个样本，定义：

- \(y^*\): gold 决策分支，建议至少四类：call / clarify / direct-answer / impossible-with-tools  
- \(t^*\): gold tool identity（仅当 \(y^*=\) call 时存在）
- \(\sigma^*\): gold canonical semantic slots，**与当前 schema 无关**
- \(\phi\): 某个 tool 的 surface interface realization（tool name、arg names、description、parameter organization、format 等）
- \(P\): candidate tool pool

### 问题定义 A：Interface Invariance under Semantic-Equivalent Schema Shift

**定义**  
在固定 \(u, y^*, t^*, \sigma^*\) 的条件下，对同一工具语义构造一组信息等价的 interface realizations \(\phi \in \Phi(t^*)\)，测量模型输出可执行 tool call 的稳定性：  
\[
Acc(f_\theta(u, P, \phi))
\]
是否对 \(\phi\) 近似不变。

**scientific object**  
不是“tool use accuracy”本身，而是 **semantic-to-interface grounding 的不变性**。

**可证伪性**  
如果在 small pool、single-turn、信息等价 schema 下，性能方差很小、model ranking 稳定，那么 interface-grounding 不是主角。

**最适合的论文类型**  
这是 **evaluation / measurement paper**。  
除非你进一步提出一个专门提升 interface-invariance 的方法，否则它不该先伪装成方法论文。

---

### 问题定义 B：Causal Bottleneck Decomposition for Function Calling

**定义**  
通过一组 oracle 干预，把 end-to-end 失败分解为三类：

1. oracle decision：给定 gold \(y^*\)
2. oracle tool identity：给定 gold \(t^*\)
3. oracle semantic slots / CIR：给定 gold \(\sigma^*\)

比较不同 oracle 下的增益，定位失败主要来自哪里。

**scientific object**  
不是 benchmark 分数，而是 **function-calling pipeline 中不同 latent subproblem 的可归因误差**。

**可证伪性**  
如果 tool-identity oracle 已经几乎完全恢复性能，说明主问题不是 interface-grounding，而更像 decision/search。  
如果 even with CIR 仍然失败，说明问题不只是 interface，也可能是 serialization、decoder control、格式遵循，甚至 evaluator mismatch。

**最适合的论文类型**  
**最强的 evaluation / measurement paper**。  
这也是我认为你现在最值得写的主问题。

---

### 问题定义 C：Schema Design as an Optimization Variable

**定义**  
把 interface realization \(\phi\) 当成可优化变量，在**不增加语义信息**、受 token budget 约束的前提下，求最 model-compatible 的 schema：
\[
\phi^* = \arg\max_{\phi \in \Phi(t)} \mathbb{E}_{\theta \sim \mathcal{M}}[Acc(f_\theta(u,P,\phi))]
\]
或最小化跨模型最坏情况损失。

**scientific object**  
不是“模型更强”，而是 **tool/interface design 本身是否是一个可优化的系统变量**。

**可证伪性**  
如果所谓“friendly schema”只是因为信息更丰富、描述更长、加入额外 task hints 才有效，那这不是 interface science，只是 prompt stuffing。

**最适合的论文类型**  
默认是 **data / interface engineering paper**。  
只有当你提出的是一个清晰的优化目标、跨模型泛化、并且严格控制信息等价，才有机会升格成 methods main-track。

---

### 问题定义 D：Controlled Multi-turn Amplification of Interface Bottlenecks

**定义**  
把同一个 single-turn task 展开成多轮澄清/补全版本，但控制最终语义不变；比较 raw history、canonical state summary、oracle state 三种条件下，schema shift 的效应是否放大。

**scientific object**  
不是一般 agent planning，而是 **interface-grounding 在最小 statefulness 下是否被放大**。

**可证伪性**  
如果 multi-turn gap 在 canonical state summary 条件下基本消失，说明你看到的是 memory/state tracking，而不是 interface。  
如果 canonical summary 仍保留大 gap，说明 same bottleneck 被 multi-turn 放大。

**最适合的论文类型**  
这是 **measurement extension**。  
不建议它做第一篇的主 framing。

---

## 2) 这些定义分别更适合哪类 paper

最强排序我会这样给：

**第一名：问题定义 B（oracle decomposition）**  
最像顶会 measurement paper。它回答的是“我们到底在测什么”，不是“我怎么又把分数抬高了”。

**第二名：问题定义 A（interface invariance）**  
也属于 measurement。它对 benchmark validity、deployment reliability、cross-model ranking 都有直接意义。

**第三名：问题定义 C（schema optimization）**  
更像 data / interface engineering。除非你把它做成“canonical semantics ↔ interface compiler”这类可泛化方法，否则容易被审成 prompt / schema rewriting trick。

**第四名：问题定义 D（controlled multi-turn amplification）**  
适合 measurement follow-up。它不是不重要，而是不干净；很容易被审稿人问“你这到底在测 interface 还是 memory/planning/state tracking”。

---

## 3) 最有判别力的实验协议

### 核心原则

第一篇只做 **single-turn、one-call 为主**。  
多步、长链、agent loop、用户模拟，一律先降到次要位置。因为你现在要识别 bottleneck，不是要追求 realism maximalism。

### 数据最小单元

每个样本必须至少带：

- gold 决策标签 \(y^*\)
- gold tool identity \(t^*\)
- gold canonical semantic slots \(\sigma^*\)
- 至少 3 个信息等价 schema variants
- 一组 unrelated distractors
- 一组 semantically related distractors
- no-call / clarify / direct-answer / impossible 子集

### 评价指标不要只报一个 overall accuracy

至少分开报：

- 决策准确率：call / no-call / clarify / direct-answer
- tool selection accuracy（conditioned on should-call）
- arg key accuracy（conditioned on correct tool）
- arg value accuracy（conditioned on correct tool）
- format / schema validity
- end-to-end executable accuracy
- no-call precision / recall
- model ranking stability（Kendall tau / Spearman）
- error taxonomy 分布

---

## 4) 四个主实验，以及每个实验到底说明什么

### 实验 1：Semantically Equivalent Schema Perturbation

**做什么**  
固定 task semantics、固定 tool pool、固定用户 query，只改 \(\phi\)：tool name、arg names、description wording、parameter order、nesting、required/optional organization、doc format。

**控制了什么**  
控制了任务语义、gold action、gold tool、gold slots、工具集合、评测器。

**排除了什么替代解释**  
配一个 **prompt paraphrase control**。如果普通 prompt 改写影响小，而 schema 改写影响大，你测到的就不是 generic prompt brittleness。BFCL V4 的公开结果正是这个方向：prompt format/style 没有稳定趋势，但 return/doc format 会明显改写结果，甚至让一些专门 tool-use 模型几乎归零。并且他们明确说这类行为在 basic single-turn setting 已经可见，不需要先上 multi-turn。[Ref 4]

**如果结果成立，支持什么**  
大幅支持 interface-grounding，尤其当错误从 wrong tool 转向 wrong arg key / wrong arg value / invalid format 时。

**如果结果不成立，意味着什么**  
在 clean single-turn regime 下，interface-grounding 不是主导因素；你不该硬讲它是 first-order。

**最大 confound**  
“friendly” 比 “hostile” 多给了信息，而不是更好接口。这个一旦发生，结论无效。

---

### 实验 2：Oracle Ladder（decision → tool → CIR）

建议至少做四个条件：

1. **Base**
2. **Oracle decision**：给 gold \(y^*\)
3. **Oracle tool identity**：给 gold \(t^*\)
4. **Oracle CIR**：给 gold \(\sigma^*\)

最好再拆出两个 tool oracle：

- **Tool-name oracle in full pool**：保留上下文 clutter，只告诉它 gold tool
- **Gold-only pool oracle**：只留下正确工具

**控制了什么**  
同一任务、同一 schema、同一 evaluator，只改变被 oracle 掉的 latent variable。

**排除了什么替代解释**  
把 “wrong tool because didn’t understand task” 和 “wrong arg because current schema mapping 失败” 拆开。

**如果结果成立，支持什么**  
- Base → oracle decision 增益大：decision bottleneck  
- decision oracle → tool oracle 增益大，且大池子更明显：search/calibration  
- tool oracle 之后仍错，而 CIR oracle 大幅恢复：interface-grounding  
- CIR oracle 下仍错：更像 serialization / strict format following / decoder control，不该再含糊叫“decision”

**如果结果不成立，意味着什么**  
如果 tool oracle 几乎已经恢复全部性能，那你的问题不是 interface，而是 decision/search。  
如果 CIR oracle 也救不回来，你的问题定义还不够干净，或者 evaluator / parser 本身在制造假错误。

**最大 confound**  
CIR 不是 tool-agnostic，而偷偷继承了 schema naming。那就不再是 canonical IR，而是 disguised schema。

---

### 实验 3：Distractor / Irrelevant Tools / No-call Stress

**做什么**  
固定 gold tool 的 friendly schema，只改 tool pool：

- 1 gold + N unrelated
- 1 gold + N semantically related
- no-call cases with tempting near-neighbor tools

**控制了什么**  
gold semantics 和 gold schema 不变；只改搜索空间和干扰项结构。

**排除了什么替代解释**  
如果不改 schema，只加 distractor，性能下降就不能再解释成 interface wording。

**如果结果成立，支持什么**  
wrong tool、over-call、under-call 随 related distractor 增大而上升，且 oracle tool identity 明显恢复，这就是 search/calibration bottleneck。已有 2025 工作已经显示 toolkit expansion 会稳定掉点，并带来 wrong function、wrong number of functions、wrong parameter assignment 等错误；更大的 open-world benchmark 也在更大工具空间下观察到明显退化。[Ref 5]

**如果结果不成立，意味着什么**  
大工具池不是主矛盾，你应该减少这条线在 framing 中的权重。

**最大 confound**  
context length 自身增长。你需要区分“搜索失败”与“长上下文注意力失败”。

---

### 实验 4：Controlled Multi-turn Amplification

**做什么**  
把 single-turn 任务拆成 2-3 轮：第一轮信息不全，第二轮补槽位，第三轮执行调用。比较：

- raw dialogue history
- canonical state summary
- oracle state summary

**控制了什么**  
最终 task semantics、gold action、gold tool、gold slots 都保持不变。

**排除了什么替代解释**  
如果 canonical state summary 把 multi-turn gap 抹平，你测到的主要是 memory/state tracking，不是 interface。

**如果结果成立，支持什么**  
- single-turn 已有 interface gap，multi-turn raw history 放大，但 canonical summary 后仍保留显著 gap：same bottleneck 被放大  
- 只有 raw history 差，canonical summary 不差：scientific object 已经变成 memory / state tracking

**如果结果不成立，意味着什么**  
multi-turn 不是必要主设定；把它降成 appendix stress test 更合理。

**最大 confound**  
turn segmentation 改变了语用线索，导致“同一语义”并不等价。

---

## 5) 你点名的几个设定，我的具体判断

### semantically equivalent schema perturbation
这是你最核心的 instrument。  
但要分两类：

- **within-tool perturbation**：tool name、arg name、description、order、nesting —— 主要测 interface-grounding
- **cross-tool perturbation**：让近邻工具在命名/描述上更相似 —— 主要测 search/calibration

别把两者混成一个“robustness”分数。

### friendly vs hostile tool definition
可以做，但 hostile 必须是 **信息等价、不是信息更少**。  
一旦 hostile 变成“更隐晦且更不完整”，你测到的是 documentation sufficiency，不是 interface-grounding。

### oracle tool identity
必须做，而且最好做两版：

- 告诉模型 gold tool name，但保留全池子
- 直接把候选池裁成 gold-only

前者去掉 selection ambiguity；后者再去掉 context interference。两者差值很有信息量。

### oracle semantic slots / canonical intermediate representation
这是最锋利的 scalpel。  
CIR 应该只表达用户语义，不表达当前 schema。比如 `date`, `city`, `unit`, `sort_order`，而不是 `travel_day`, `geo_target` 这种 schema-specific key。

### distractor / irrelevant tools
不要只加 irrelevant tools。  
**related distractors** 才是 search/calibration 的主战场；irrelevant 只是下界。

### no-call / should-not-call
必须升格成主任务，不是 appendix。  
而且最好不是二分类，而是至少四分类：call / clarify / direct-answer / impossible-with-tools。When2Call 的启发就在这里：binary no-call 太粗，会把“缺槽位应追问”和“根本不该调用”混在一起。[Ref 6]

### ranking changes across models
这是你 paper 的一个强 readout。  
如果 semantically equivalent schema 就能改写 model ranking，那说明现有 leaderboard 至少部分在测 **interface compatibility**，而不是纯 latent tool-use competence。

### error taxonomy
你的 taxonomy 很关键，但必须配合 oracle 才能解释：

- wrong tool：decision 或 search
- wrong arg key：强 interface-grounding 信号
- wrong arg value：**不能直接判 interface**，要看 CIR oracle 是否能修复
- over-call / under-call：decision + calibration
- wrong number of calls：如果进入 multi-call，就开始沾 planning

---

## 6) 你那几个关键判断，我直接回答

### 如果 single-turn 已经能证明 interface-grounding 是主要瓶颈，最强 framing 是什么？

不是“robustness to schema perturbation”。  
更强的 framing 是：

**Current function-calling evaluation conflates semantic tool-use competence with arbitrary interface realization; under semantically fixed single-turn tasks, a substantial share of failures is caused by interface-grounding rather than latent decision deficiency.**

这会把论文从“一个鲁棒性小技巧”抬成“我们之前测错了东西”。

---

### 如果必须扩展到 multi-turn 才能让问题成立，为什么？

只有一种正当理由：  
**你要研究的 interface phenomenon 只有在跨轮状态累积时才出现。**

例如：

- 用户分两轮给槽位，最后一轮才调用
- 上一轮工具输出需要在下一轮映射成新工具输入
- 用户会修正先前槽位，模型要重新 ground 到同一接口

如果不是这种情况，single-turn 已经足够。

---

### 一旦扩展到 multi-turn，哪些还属于 tool/interface，哪些已经变成别的问题？

**还属于 tool/interface 的：**

- 同一 canonical state 如何映射到当前工具 schema
- 工具输出如何被 canonicalize 成后续输入
- schema wording 如何影响跨轮重用同一工具

**已经变成 planning / memory / state tracking / credit assignment 的：**

- 该先查哪个工具、再查哪个工具
- 记住用户之前说过的约束
- 响应用户中途改目标
- 与用户协作修改共享世界状态
- 用 delayed reward 学这些行为

---

### multi-turn 和 agent RL 是在“暴露同一瓶颈”，还是在“改变 scientific object”？

**答案是：默认在改变 scientific object。**

只有在你把 state 规范化、把 planning 降到最低、把 history 变成 canonical summary 时，multi-turn 才能算“同一瓶颈的 stress test”。

至于 agent RL，几乎更明显是在改 object。最近多轮 RL 论文自己就把问题表述成 sparse rewards 和 turn-level credit assignment；那是一个完全独立的优化问题，不是 interface definition 问题。[Ref 7]

---

### 在什么条件下，single-turn 是更干净、更强的切入点？

当你的核心问题是：

- tool/function definition 是否 first-order
- schema wording / naming / organization 是否决定成败
- current leaderboards 是否把 interface compatibility 当成了 competence

这三个问题，single-turn 是最强切口，因为它最容易把 planning、memory、state tracking 排除掉。BFCL v4 的 format-sensitivity 甚至明确只用 single-turn 子集就论证这类现象。[Ref 4]

---

### 在什么条件下，必须把 multi-turn 纳入主问题才有说服力？

当你要 claim 的不是“schema matters”，而是：

- 用户意图天然跨轮分布
- 工具输出到下轮输入的 canonicalization 是核心
- 单轮看不见的 slot update / correction 是主要失败来源

这时 multi-turn 才应进入主问题。

---

## 7) 最终判断：先 single-turn 干净识别，再扩到 multi-turn / agent RL

我的判断非常明确：**先做 single-turn clean identification。**

理由有四个：

1. **你的科学问题本质上是 attribution，不是 optimization。**  
2. **2025+ 文献已经说明 multi-turn 会强烈引入 orthogonal bottlenecks。**  
3. **single-turn 已经足够构造强反事实：schema perturbation、oracle tool identity、oracle CIR、no-call。**  
4. **如果 single-turn 里都证明不了 interface 是 first-order，multi-turn 只会让你更难证明。**

所以顺序应该是：

- **Paper 1**：single-turn causal decomposition  
- **Paper 2**：controlled multi-turn amplification  
- **Paper 3**：如果再往前走，才考虑 training / RL / agent optimization

---

## 8) 如果最后证明 interface definition 确实是 first-order bottleneck，最自然的方法路线

### 路线 1：Canonical Semantic IR + Schema Compiler
**自然性**  
直接从 oracle CIR 实验推出。  
如果 gold CIR 能大幅恢复性能，那么最自然的方法就是把 tool use factorize 成：

1. user → canonical semantic slots  
2. canonical slots → current schema compilation

**这可能是新的 scientific object**  
因为你真正建模的是 “semantic tool intent” 与 “interface realization” 的解耦。

**不是小技巧的条件**  
IR 必须 tool-agnostic，且在 held-out schema families 上泛化。

---

### 路线 2：Interface-Invariant Training / Multi-view Schema Learning
**自然性**  
直接从 semantic-equivalent schema perturbation 推出。  
同一语义、多个 schema views，本来就是最自然的 invariance training 数据。

**什么时候只是 recipe**  
如果你只是“把更多 schema variant 混进 SFT”，那只是 data augmentation。

**什么时候可能是方法论文**  
如果你显式学习 semantic latent，并对不同 schema views 做一致性约束，那就有方法性了。

---

### 路线 3：Automated Schema Optimization / Model-Compatible Interface Synthesis
**自然性**  
直接从 friendly vs hostile tool definition 推出。  
如果 interface 真是 first-order，当然应当优化 interface 本身。

**大多数情况下它只是 engineering**  
这条线很容易退化成 schema rewriting / naming trick。PA-Tool、Play2Prompt 这类工作都说明它有用，但默认更像 interface engineering baseline，而不是主 scientific object。NLT 也是强 baseline，但它同时改变了输出模态、架构分工和 token budget，所以不能拿来直接证明“interface-grounding 就是主因”。[Ref 8]

---

## 9) 论文包装：我建议你这样打

### 最强的一句话问题定义
**在语义固定的 function-calling 任务中，LLM 的可执行工具调用是否对任意等价的 tool/interface realization 保持稳定；如果不稳定，主要误差来自 decision、interface-grounding，还是 search/calibration？**

### 最强的标题方向
**When Tool Use Fails at the Interface: A Causal Decomposition of Decision, Interface-Grounding, and Search in Function Calling**

### 最强的主 claim
**Current function-calling systems and benchmarks conflate semantic tool-use competence with arbitrary interface realization. In clean single-turn settings, semantically equivalent schema changes cause large accuracy and ranking shifts, and oracle decomposition shows that a substantial portion of failures arises from interface-grounding rather than latent decision deficiency alone.**

### 最小可发表实验矩阵
我会要求至少有：

- 4 类决策标签：call / clarify / direct-answer / impossible
- 3 类 schema 条件：friendly / hostile-within-tool / hostile-cross-tool
- 3 个 oracle：none / tool identity / CIR
- 2 个 pool 条件：small / distractor-heavy
- 1 个 prompt paraphrase control
- 4–6 个模型，至少覆盖 frontier + open

### 关键主表设计
**主表 1：Bottleneck decomposition**
- rows: models
- cols: base, +oracle decision, +oracle tool identity, +oracle CIR
- 每组再分 friendly / hostile
- 右侧附 error taxonomy：wrong tool / wrong arg key / wrong arg value / over-call / under-call

**主表 2：search/calibration stress**
- rows: models
- cols: unrelated distractors, related distractors, no-call precision/recall, ranking stability

### 最关键的一张图
**一张 oracle-recovery waterfall 图。**  
横轴：base → oracle decision → oracle tool identity → oracle CIR  
纵轴：accuracy  
分别画 friendly / hostile / distractor-heavy 三条曲线。

这张图会直接回答：  
到底是 decision 在救火，还是 interface 在掉链子，还是 search 在作祟。

### clear kill / go criteria

**Go：继续主打 interface-first-order**
- 在 small-pool、single-turn 下，friendly vs hostile 的 paired drop 明显大于 prompt paraphrase control
- tool oracle 后仍保留大量 hostile gap
- CIR oracle 能恢复这部分剩余 gap
- 错误主要转移到 arg key / value / format，而不是 wrong tool

**Kill：不要硬打 interface-first-order**
- schema perturbation 效应很小，或只在极小模型上出现
- hostile gap 基本被 tool oracle 一步消掉
- distractor / no-call 比 schema variation 解释更多方差
- model ranking 在等价 schema 下高度稳定

---

## 10) 哪些 framing 看起来像论文，其实很弱

### “只是 robustness recipe”
“我们加了 schema variants 训练，鲁棒性提高了。”  
这不够。没有 attribution，就只是 augmentation。

### “只是 schema augmentation”
“我们把 tool name / description 改写得更友好，分数提升。”  
这默认是 interface engineering，不是 scientific object。

### “只是 prompting / rewriting trick”
“我们让另一个 LLM 重写 tool docs。”  
默认是 prompt optimization。除非你证明它系统性减少的是 interface-grounding，而不是多给了 hints。

### “只是 benchmark stress test”
“我们加 distractors / multi-turn / bigger tool pool，模型掉分。”  
这只说明任务更难，不说明 **为什么** 更难。

---

一句更尖锐的总结：

**你现在最应该写的，不是“tool-use methods paper”，而是“what current function-calling benchmarks are actually measuring” 的论文。**  
如果 single-turn 下都能把 interface-grounding 定位成 first-order，那么这篇 paper 的价值会比大多数 agent-RL 方法更硬，因为它直接决定后续方法论文到底该优化哪里。

## References

### Ref 1
- https://arxiv.org/abs/2504.18851
- https://gorilla.cs.berkeley.edu/blogs/17_bfcl_v4_prompt_variation.html
- https://aclanthology.org/2025.trustnlp-main.20.pdf
- Original token: `citeturn983770view0turn287915view0turn983770view4turn906712search1turn983770view2turn587031view1turn368952view0turn642361view0turn745618view4`

### Ref 2
- https://openreview.net/forum?id=2GmDdhBdDk
- Original token: `citeturn903376view0turn745618view0turn647093view2turn428850view0turn892374view0`

### Ref 3
- https://arxiv.org/html/2502.00032v1
- Original token: `citeturn510969view0turn648269view5`

### Ref 4
- https://gorilla.cs.berkeley.edu/blogs/17_bfcl_v4_prompt_variation.html
- Original token: `citeturn983770view4`

### Ref 5
- https://aclanthology.org/2025.trustnlp-main.20.pdf
- Original token: `citeturn587031view1turn587031view2turn368952view0turn642361view0`

### Ref 6
- https://arxiv.org/abs/2504.18851
- Original token: `citeturn983770view0`

### Ref 7
- https://arxiv.org/abs/2604.02869
- Original token: `citeturn398872search0`

### Ref 8
- https://arxiv.org/html/2510.07248v2
- Original token: `citeturn147617view1turn866055view0turn147617view0`

## Deduplicated Links

- https://arxiv.org/abs/2504.18851
- https://gorilla.cs.berkeley.edu/blogs/17_bfcl_v4_prompt_variation.html
- https://aclanthology.org/2025.trustnlp-main.20.pdf
- https://openreview.net/forum?id=2GmDdhBdDk
- https://arxiv.org/html/2502.00032v1
- https://arxiv.org/abs/2604.02869
- https://arxiv.org/html/2510.07248v2
