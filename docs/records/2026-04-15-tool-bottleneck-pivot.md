# 2026-04-15 Tool Bottleneck 路线重定义

## 背景

用户基于外部 `GPT-5.4-pro` 做了一轮新的高强度问题重定义，结果保存在：

- `docs/fc_pdf/tool-function-bottleneck-analysis.md`

这次外部 challenge 的核心作用，不是直接给方法，而是重新回答：

- 当前 function calling 到底在什么地方失败？
- 失败主要属于：
  - `decision`
  - `interface-grounding`
  - `search/calibration`
  中的哪一类？
- `multi-turn / agent RL` 到底是在放大同一个瓶颈，还是已经把 scientific
  object 换掉了？

## 当前采纳的主判断

### 1. 第一篇不再默认是 methods-first

当前最强的第一篇论文，不再默认写成：

- `schema-reusable decision representation`
- `reuse_main`
- `A->B` fixed-`d` method paper

当前更合理的第一篇定位是：

- `single-turn`
- `semantic task fixed`
- `tool pool controlled`
- `causal measurement paper`

目标不是先提方法，而是先做对 bottleneck attribution。

### 2. 当前主 scientific object 已切到 bottleneck decomposition

新的主问题是：

> 在干净的 function-calling 设定下，当前系统的主要失败来自
> `decision`、`interface-grounding`，还是 `search/calibration`？

更具体地说，当前最值得验证的是：

> `tool/function definition` 是否已经是 first-order bottleneck。

### 3. multi-turn / agent RL 暂时降级

当前不把：

- `multi-turn`
- `agent RL`
- `long-horizon planning`

当成第一篇的主对象。

原因不是这些问题不重要，而是：

- 它们会强烈引入：
  - memory
  - state tracking
  - planning
  - coordination
  - credit assignment
- 会让 interface 问题变得更难识别和归因

当前更合理的定位是：

- `single-turn`：做干净识别
- `multi-turn`：后续 stress setting / amplification setting
- `agent RL`：更后面的优化问题，不是当前第一篇的 scientific object

## 这对仓库里已有工作的影响

### 不是“之前都白做了”

之前的工作没有白做，但角色变了。

当前最有价值的可复用资产：

- paired-schema 数据构造链路
  - 现在可直接作为 `semantically equivalent schema perturbation`
    instrument
- exact tool-call evaluator
  - 仍然适合作为 executable / exact correctness 口径
- xLAM single-call baseline runtime
  - 仍然是 baseline bring-up、数据清洗、模型行为观察的入口
- `schema_augmented` / `hammer_like` baseline bring-up 结果
  - 仍然能说明当前 direct baseline 的强弱和局限

### 但这些东西不再等于主论文证据

当前仓库里还缺下面这些关键东西，才能真正支撑新的 measurement 主线：

- 显式决策标签：
  - `call`
  - `clarify`
  - `direct-answer`
  - `impossible-with-tools`
- `oracle tool identity`
- `oracle semantic slots / CIR`
- related distractor tool pools
- 更清晰的 error taxonomy
- 跨模型 ranking change 分析

## 当前最合理的论文推进顺序

### 阶段一：先做 clean single-turn measurement

先用单轮、可控工具池、语义固定的任务，把三类瓶颈拆开：

- `decision`
- `interface-grounding`
- `search/calibration`

### 阶段二：如果 interface 真的是 first-order，再决定是否做方法

只有当 clean measurement 清楚表明：

- interface-grounding 的 effect 很大
- 而且不是 search / decision 假扮的

才值得认真投入方法线。

### 阶段三：multi-turn 只做放大验证

如果后面要扩到多轮，当前推荐写法是：

- multi-turn 不是新的主问题
- 它只是用来检验同一个 interface bottleneck 会不会被放大

## 对旧路线的当前定位

旧路线不是彻底删除，而是降为：

- secondary route
- contingent route

也就是：

- 如果 measurement 结果说明 interface/transfer gap 明显且稳定，
  再重新讨论 `reuse_main`
- 如果 measurement 结果说明问题更像 benchmark validity / interface
  compatibility，那么更合理的是 measurement/evaluation 论文，而不是
  methods-first 论文

## 当前推荐阅读顺序

1. `docs/fc_pdf/tool-function-bottleneck-analysis.md`
2. `docs/fc_pdf/tool-function-bottleneck-analysis-interpretation.md`
3. 本文档
4. `STATUS.md`
5. `HANDOFF.md`
