# NeurIPS 2026 Function Calling Idea Draft V2

## 1. 目标

这份 `v2` 不是在原 draft 上做小修，而是基于最近一轮 thesis 裁决后的**主线收缩版**。

与这份 scientific draft 配套的执行文档在：

- `docs/superpowers/plans/2026-04-08-schema-reuse-pilot-v1-implementation-plan.md`

目标只有一个：

**先把论文主命题收敛成一个更窄但更可辩护的 function-calling 方法问题。**

当前版本的核心原则：

- 主题仍然必须是 `function calling / tool use`
- 不做大而全的 agent framework
- 不把 `execution-feedback posterior distillation` 当作当前主线
- 不把 `RL` 放进当前主线
- 先证明是否存在一个**可跨等价 schema 复用的 decision representation**

## 2. 最终裁决

`v2` 的最终收敛是：

- **主 thesis**：`cross-schema decision reuse / schema-reusable decision representation`
- **主证据链**：`counterfactual decoding + d-intervention controls`
- **phase-2 extension**：`execution-feedback posterior distillation`
- **当前不进主线**：`RL`

一句话版：

**这篇论文先不回答“feedback 应不应该更新 latent posterior”，而先回答“是否存在一个可在等价 schema 间 encode once, ground many times 的 decision object”。**

补充裁决：

- 最近一轮 `GPT-5.4 Pro` 严审的结论是：`claim 2 / execution-feedback posterior distillation` 当前最多只能作为 **secondary claim**
- 除非后续补出严格的 `same-information budget + frozen rollout + matched-latent token baseline + A_feedback->B` 证据链，否则不应重新升格为主贡献

## 3. 这篇论文现在到底解决什么问题

`v2` 解决的问题比原稿更窄：

**现有 function-calling 模型经常把表面 schema 当成决策对象的一部分，因此在 tool renaming、argument renaming、description paraphrase、输出格式变化、tool pool 扩张等情况下出现系统性退化。**

更精确地说，这篇论文现在只关心下面这个问题：

**同一个语义决策，能否在一组双射等价的 schema 之间被复用，而不是每换一个 schema 就必须重新学一遍表面调用形式。**

这不是在解决：

- 长时 agent planning
- 通用 credit assignment
- 大规模 RL tool optimization
- reranking / best-of-n selection

## 4. 主 thesis

当前最值得押的主 thesis 是：

**function calling 的正确学习目标不是 schema-bound tool-call tokens，而是一个能够在等价 schema 间复用、再由当前 schema 完成 grounding 的 decision representation。**

更形式化地写：

- `d = E(s, T_A)`
- `y_A = D(d, s, T_A)`
- `y_{A->B} = D(d, s, T_B)`

其中 `T_B = g(T_A)`，`g` 来自严格定义的等价 schema 变换族 `G`。

如果 `d` 真的是 decision object，而不是压缩码，那么：

- 在不重新编码的情况下，`y_{A->B}` 仍应接近正确
- 且显著优于 `shuffle d` 与 `null d` 对照

## 5. 为什么主线必须收窄到这里

原稿最大的问题不是想法太少，而是把三件事绑得太紧：

- latent decision / bottleneck
- feedback-conditioned posterior distillation
- schema robustness / evaluation protocol

一旦三者同时做主叙事，reviewer 很容易把论文切成：

- CoLA / latent action 的变体
- SDPO / OpenClaw 风格 hindsight distillation 的换空间版本
- Hammer / robustness benchmark 的组合工作

所以 `v2` 的原则是：

- **先证 decision reuse 是否存在**
- 只有在这个核心对象成立后，才值得继续问 feedback 或 RL 应该如何作用在它上面

## 6. 最小方法定义

### 6.1 严格定义等价 schema 变换族 `G`

当前只承认下列等价变换：

- tool renaming
- argument renaming
- description / documentation paraphrase
- 少量可逆的 argument reshaping

硬约束：

- 每个 `g ∈ G` 都必须可构造双射映射
- ground-truth call 必须可同步映射到目标 schema
- 若用户文本显式包含 tool / argument surface form，则必须过滤或做一致替换

但为了让 `v2` 能被尽快证伪，`pilot-v1` 的主表不应一次性吃下整个 `G`。

`pilot-v1` 只把下面三类变换放进主论证：

- 随机 opaque tool renaming
- 随机 opaque argument renaming
- schema key reorder

原因很直接：

- 这三类最接近严格双射
- 最容易避免 task drift
- 最适合作为 `counterfactual decoding` 的主战场

下面这些不应进入 `pilot-v1` 主表：

- description paraphrase
- argument reshaping
- return format / prompt style 变化

它们可以保留到 `stage-2 robustness`，但不能在最早期 pilot 里和主命题绑死，否则 reviewer 很容易说我们测到的是 format effect、doc quality effect 或 distribution shift，而不是 `decision reuse`。

### 6.2 编码与 grounding

最小结构只有两层：

- `E(s, T) -> d`
- `D(d, s, T) -> y`

其中：

- `s` 是用户请求、对话上下文、已有工具返回等状态
- `d` 是当前步的 decision representation
- `y` 是最终可执行 tool call

这里不预设 `d` 必须是离散 codebook。

`v2` 的默认偏好是：

- 先用**小容量连续 bottleneck**
- 只要足够限制信息通量即可
- 不把 codebook 设计本身写成论文亮点

### 6.3 训练协议

对每个样本构造 `(s, T_A, T_B = g(T_A), y_A, y_B)`。

训练时最关键的不是再编码一次 B，而是：

1. 在 A 下编码：`d_A = E(s, T_A)`
2. 在 A 下正常 grounding：`y_A = D(d_A, s, T_A)`
3. 在 B 下**不重编码**做 counterfactual grounding：
   - `y_{A->B} = D(d_A, s, T_B)`
4. 可选地做 B 侧正常编码上界：
   - `y_{B->B} = D(E(s, T_B), s, T_B)`

最小 loss 只保留：

- `L_call(A)`
- `L_call(A->B)`
- `L_consistency` 或同类 reuse regularization

`v2` 不保留：

- hindsight posterior module
- posterior matching loss
- feedback-conditioned teacher
- RL calibration

## 7. 核心证据链

这篇论文的证据链现在非常明确：

### 证据 1：Counterfactual Reuse

主指标：

- `CF-ExecAcc`
- `CF-ASTAcc`
- `CF-Gap = Acc(B->B) - Acc(A->B)`

### 证据 2：`d`-intervention controls

必须包含：

- `shuffle control`
- `null control`

要求：

- `A->B` 明显优于 `shuffle/null`
- 否则不能声称 `d` 承载了可复用 decision

### 证据 3：Held-out schema transforms

必须证明：

- 不是只在 seen renaming 上成立
- 而是在 held-out 变换或 held-out schema family 上也有稳定收益

## 8. 最小 pilot

### 8.1 Pilot 目标

当前 pilot 只回答一个问题：

**是否存在一个可辩护的 schema-reusable decision object。**

### 8.2 Pilot 数据

优先：

- single-turn
- audit-aware
- paired-schema synthetic transforms

不建议一开始就上：

- BFCL-v3 multi-turn 主战场
- 复杂长轨迹
- 强依赖在线环境的 RL 流程

更具体地说，`pilot-v1` 的数据切片应满足下面四个条件：

- 每条样本都应有确定或近确定的 executable / AST-verifiable tool call
- 每条样本都应尽量接近单步决策，而不是长链规划
- 用户请求里不应显式泄露 tool / argument surface form；若出现，必须做一致替换或过滤
- train / dev / test 应先按底层任务语义切分，再在各 split 内生成 paired schemas，不能先做变换再随机切分

对 BFCL 的使用建议也要写死：

- BFCL 更适合作为主评测来源，而不是主训练源
- `pilot-v1` 只使用经过人工抽检或 audit-aware 过滤的 single-turn executable slice
- BFCL-v3 multi-turn 不进入主表，只能做后续附录或 phase-2 sanity check

### 8.3 Pilot baselines

当前最小足够集合：

- Vanilla SFT function-calling baseline
- schema-augmented direct SFT baseline
- Hammer-style schema masking / robustness baseline
- matched-capacity latent bottleneck baseline without reuse loss
- latent-consistency-only baseline

这里**不把**下面这些放进 `v1` 主矩阵：

- token-hindsight baseline
- EFPD baseline
- `+RL` 版本
- rerank / verifier / best-of-n
- PA-Tool / schema adaptation style baseline

原因不是它们永远不重要，而是它们会把 pilot 的问题从“decision object 是否存在”扯成“哪种学习信号更强”。

上面五个 baseline 的分工要非常明确：

- `Vanilla SFT` 回答“普通 function-calling 直接学 tokens 的上限大概在哪里”
- `schema-augmented direct SFT` 回答“是不是更强 augmentation 就够了”
- `Hammer-style` 回答“是不是 masking / robustness recipe 就够了”
- `matched latent bottleneck` 回答“是不是 latent head 本身就够了”
- `latent-consistency-only` 回答“是不是把两个 latent 拉近就够了，而不需要 fixed-`d` reuse 训练”

如果这几个 baseline 都没被拉开，`v2` 就没有必要继续往主论文推进。

但这里必须补一个协议边界：

- `schema-augmented SFT` 与 `Hammer-style` 这类 direct baselines，并不天然拥有与 reuse_main 对称的 fixed-`d` `A->B` 接口
- 因此它们不应直接进入“reuse-identifiability 主表”的 `A->B` 同栏比较，除非后续真的能定义出严格对称的 `A->B` protocol
- 它们更合适的角色是进入另一张 `robustness-payoff` 表：在 held-out target schema 直接呈现给模型时，比较谁的实际泛化收益更强

换句话说，pilot-v1 要回答的是两个不同问题：

- **问题 R：是否存在可被 fixed-`d` counterfactual grounding 使用的 reusable decision representation**
- **问题 P：这种训练原则是否最终带来比 direct robustness recipe 更强的 held-out schema 泛化收益**

这两个问题必须分表报告，不能混成一张表。

### 8.4 Pilot 变换协议

为了让主命题尽量少受混淆，实验里必须区分三类变换集合。

#### `G_main`：主命题变换

只包含：

- tool renaming
- argument renaming
- schema key reorder

要求：

- 重命名使用训练期与测试期**词表不重叠**的随机 opaque strings
- test 期使用 held-out transform seeds，不能复用训练期同一映射模板
- `A->B` 的所有比较都在相同解码超参与 evaluator 下完成

#### `G_ext`：扩展等价变换

只在 `G_main` 已经跑通后再加入：

- description paraphrase
- 少量可逆 argument reshaping

这部分的定位是：

- 增强论文外延
- 不承载 `v2` 生死

#### `H_robust`：支持性 robustness probes

不属于等价 schema 证明本身，但可以作为支持性实验：

- irrelevant tools injection
- enlarged tool pool

它们的作用不是证明 `decision reuse`，而是证明这个 decision object 在更现实的 tool selection 干扰下仍有用。

### 8.5 Pilot 主表、指标与上界

`pilot-v1` 现在应明确拆成两张表。

#### 表 R：Reuse-Identifiability 主表

这张表只允许放入能够定义 fixed-`d` `A->B` 的方法：

- reuse_main
- matched latent bottleneck
- latent-consistency-only

它不应该只报普通 `ExecAcc`，而应强制包含下列六列：

- `A->A`
- `B->B`
- `A->B`
- `shuffle d`
- `null d`
- `CF-Gap = Acc(B->B) - Acc(A->B)`

其中：

- `A->A` 用来保证模型并没有因为引入 bottleneck 而把基础 function-calling 做坏
- `B->B` 是在目标 schema 下允许重新编码的上界
- `A->B` 才是主 claim 的核心
- `shuffle/null` 是 `d` 是否真的在驱动 grounding 的必要对照

#### 表 P：Robustness-Payoff 主表

这张表允许放入所有方法：

- Vanilla SFT
- schema-augmented direct SFT
- Hammer-style
- reuse_main

它回答的不是 fixed-`d` reuse 是否存在，而是：

- 在 held-out target schema 直接呈现给模型时
- reuse-oriented training 是否比 direct robustness recipe 带来更好的实际泛化收益

因此这张表的核心指标应是：

- `heldout_B_exec_acc`
- `heldout_B_ast_acc`
- `heldout_B_gap`（相对 train-like schema 或 `A->A`）

主指标优先级应是：

1. `CF-ExecAcc`
2. `CF-ASTAcc`
3. `CF-Gap`

推荐的表格结构是：

- 表 R：`A->A / B->B / A->B / shuffle / null / CF-Gap`
- 表 R 分解：`rename-only`、`rename+arg`、`rename+arg+reorder`
- 表 P：各方法在 held-out target schema 上的实际泛化结果
- held-out 表：训练期未见 alias vocabulary、未见 transform seed、未见 transform composition
- robustness 表：`H_robust` 下的 irrelevant tools injection 与 enlarged tool pool

这里必须显式写死：

- direct baselines 若没有严格对称的 fixed-`d` `A->B` 接口，则不得与 reuse_main 共用表 R
- `B->B` 只能作为 ceiling 与可解释性检查，不能冒充主结果

### 8.6 Pilot 统计与预算约束

虽然 `v2` 暂时不做 `same-budget claim-2`，但 `pilot-v1` 仍然必须做最基本的公平约束。

最低要求：

- 所有 baseline 使用同一个 backbone model
- 若 latent 方法引入新增可训练参数，direct baselines 也应给到参数量级匹配的 adapter，或至少单独报告新增参数量
- 所有 baseline 对齐总训练样本量与 paired-schema 暴露次数
- 所有 baseline 对齐 optimizer steps 或近似训练 FLOPs
- 所有方法使用同一解码策略、同一最大输出长度、同一 repair 次数
- pilot 阶段关键结果至少跑 `3` 个随机种子，并报告 mean ± 95% CI 或 standard error

必须避免的偷跑方式：

- 只给某个方法更多 schema augmentation
- 只给某个方法更多 tool-pool 干扰暴露
- 只给某个方法更长的解码预算
- 让 `B->B` oracle 结果冒充主结果

### 8.7 Pilot Go / No-Go 标准

这里最好直接写内部门槛，而不是模糊地说“看起来更好”。

建议的内部继续阈值是：

- `A->B` 必须显著高于 `shuffle d` 与 `null d`，内部参考阈值是至少 `+10` 个绝对点
- `B->B` 必须达到可解释性底线；若目标 schema 自身学不起来，则该 split 的 `A->B/CF-Gap` 不得用于正面结论
- 相对 `matched latent bottleneck` 与 `latent-consistency-only`，`CF-Gap` 至少应有明确下降；内部参考阈值是相对下降 `20%` 或绝对下降 `3` 点以上
- 在 `rename+arg` 这个子集上，`A->B` 至少也要稳定高于 `shuffle/null`
- 在 held-out target schema 的表 P 上，reuse_main 至少要稳定优于 `schema-augmented SFT` 与 `Hammer-style`
- `A->A` 不能出现明显代价；内部参考阈值是相对 `Vanilla SFT` 的下降不超过 `1-2` 点

如果只能在 seen renaming 上赢，或者一到 held-out alias / `rename+arg` / enlarged tool pool 就消失，那么这篇论文就不该继续按 `decision reuse` 写。

### 8.8 如果 pilot 失败，具体怎么改方向

为了避免“实验不理想但继续硬写”，最好把 pivot logic 提前写清楚。

可能出现的失败形态与对应动作是：

- 如果 `A->B` 不能明显高于 `shuffle/null`：
  说明 `d` 没有被 decoder 真正使用，应暂停 latent-decision thesis，而不是继续堆模块
- 如果只比 `Vanilla SFT` 强，但打不过 `schema-augmented SFT` 或 `Hammer-style`：
  说明收益更像 robustness recipe，而不是新的 decision object，应改写成更窄的 schema-robust function-calling work，或直接放弃
- 如果 `matched latent bottleneck` 与 `latent-consistency-only` 已经覆盖主要收益：
  说明 fixed-`d` counterfactual reuse 训练并非关键增量，当前 thesis 不够硬
- 如果收益必须依赖后续 `feedback / RL` 才出现：
  说明论文主命题已从 `decision reuse existence` 漂移到 `feedback learning` 或 `RL calibration`，应重新立项，而不是硬保留 `v2`

## 9. 当前论文的 2-3 个亮点应该怎么写

如果 `v2` 成立，亮点只保留三个：

### 亮点 1：更窄但更硬的问题定义

把 function calling 重写成：

- encode a reusable decision once
- ground it under equivalent schemas

而不是直接预测 schema-bound tool-call tokens。

### 亮点 2：新的方法约束

训练目标不只是“在每个 schema 上都做对”，而是要求：

- 同一个 `d`
- 在 `T_A` 与 `T_B` 下都能被正确 grounding

### 亮点 3：新的证据链

通过：

- `A->B` counterfactual grounding
- `B->B` 上界
- `shuffle/null d` 介入对照

证明模型内部存在一个会在 counterfactual grounding 中被因果使用、并且比 matched latent baselines 更可复用的中间决策变量。

## 10. 明确不在主线里的东西

下面这些都不再属于 `v2` 主线：

### 10.1 EFPD

`execution-feedback posterior distillation` 不再是主 claim。

它的定位变成：

- `phase-2 extension`
- 只有在 `decision reuse` 已经站住之后，才值得重新加入
- 即便重新加入，当前最强可辩护定位也只是：**secondary claim under strict budget**

更具体地说，下面这些条件缺一不可：

- 使用严格、封闭、schema-name-free 的 feedback ledger
- 冻结 rollout 来源，所有方法吃同一批 `(s, T_A, T_B, \hat y_A, f_A)` 元组
- 增加 `matched-latent token-hindsight` 对照，避免把收益误判为 latent 容量优势
- 至少做一次 `A_feedback->B` 的 transfer 评测，而不是只报 same-schema repair

在这些条件没有满足前，不应声称：

- `execution feedback should generally refine decision posterior rather than tokens`
- `posterior distillation` 是当前论文的 headline contribution

### 10.2 RL

`RL` 当前不进主线。

原因不是 RL 不可能有用，而是：

- 现在的核心问题不是 reward design
- 而是 decision object 是否真实存在

如果 no-RL 情况下连 `A->B` reuse 都证明不了，那么加 RL 只会把 thesis 掩盖掉，而不会把它证明出来。

### 10.3 Multi-candidate rerank

暂时移出主线。

除非后续误差分析明确显示失败主要来自多策略选择，否则不应提前引入。

## 11. 未来可以怎么把 EFPD 和 RL 捞回来

如果 `v2` pilot 通过，后续扩展顺序应是：

### Phase 2：EFPD

只在下面条件都满足时再加入：

- reuse 证据已经成立
- `d` 的作用已被 `shuffle/null` 证实
- 有能力做严格 same-budget ledger
- 有能力把 feedback 严格收缩到 runtime-only、deterministic、schema-name-free 的预算
- 有能力同时训练 `Token-Hindsight-Strong` 与 `Latent+Token-Hindsight` 两个公平对照

此时再问：

**feedback 更新 `d` 是否比更新 token 更可迁移。**

如果未来真的做这一阶段，最小公平矩阵应收缩成：

- `Decision-NoFB`
- `Token-Hindsight-Strong`
- `Latent+Token-Hindsight`
- `Decision-PD`

并且主问题不再是“有没有修好 A”，而是：

- `A_feedback->B` 是否优于强 token baseline
- `shuffle/null` updated `d` 后是否明显坍塌
- 收益是否只在 `FB-1` 这种严格 budget 下仍然成立

### Phase 3：RL

只在下面条件都满足时再加入：

- `v2` 已经证明存在可复用 decision object
- `phase-2` 或无反馈版本已经形成稳定 base
- 加 RL 回答的是 calibration / efficiency / recovery，而不是 thesis 生死

## 12. Kill Criteria

以下任一成立，`v2` 就应该暂停或改写：

- `A->B` 不明显高于 `shuffle/null d`
- `B->B` 自身不具备可解释性，导致 `CF-Gap` 失去意义
- `CF-Gap` 相对 matched bottleneck baseline 与 `latent-consistency-only` 都没有实质下降
- 在 `rename+arg` 子集上，`A->B` 不能稳定高于 `shuffle/null`
- 收益只存在于 seen renaming，而在 held-out alias vocabulary、held-out transform seeds 或 transform composition 上消失
- 在 held-out target schema 的实际泛化上，对 `schema-augmented SFT` 与 Hammer-style baseline 都没有明显优势
- 一到 audit-aware 子集、irrelevant tools injection 或 enlarged tool pool，优势就快速消失
- 为了得到收益不得不把 `d` 做得很大，导致它更像高容量压缩码而不是受约束的 decision object
- direct baselines 与 reuse_main 的比较协议始终无法写成 apples-to-apples，导致 Claim B 没有可判决性

更重要的是：

- 如果 pilot 的最终结论只是“做点 rename augmentation + masking 会更稳”，那这不是当前 `v2` 想写的论文
- 如果 pilot 的最终结论是“latent head 有用，但 fixed-`d` reuse 不是关键”，那也不是当前 `v2` 想写的论文

## 13. 当前最值得坚持的一句话

**先证明同一语义 decision 能否在等价 schema 间被复用；在这之前，不要把 posterior distillation 和 RL 当成主创新。**
