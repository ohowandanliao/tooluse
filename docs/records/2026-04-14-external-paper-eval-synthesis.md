# 2026-04-14 外部论文评估结果整合与当前决策

## 背景

用户已经基于外部 `GPT-5.4-pro` 调研，整理出一份 markdown：

- `docs/fc_pdf/function-calling-paper-evaluation.md`

这份文档不是当前仓库自己的实验结果，而是一次**高质量外部 challenge / 审稿人视角评估**。  
它的作用不是替代本地验证，而是帮助当前 repo 更早收束路线、降低后续无效实现风险。

## 当前整合结论

结合当前仓库已有判断，这份外部评估和本地路线是**同向强化**关系，而不是推翻关系。

当前明确采纳下面几条：

### 1. `schema_augmented` 不能作为 NeurIPS 2026 主创新

- 它当前应被视为：
  - 强 baseline
  - robustness / recipe 路线
  - data-centric 改善
- 它**不应**被包装成当前 repo 的主 scientific object。

当前落地结论：

- `schema_augmented` 继续保留并认真跑；
- 但它在论文里默认属于 direct baseline，而不是 headline contribution。

### 2. 当前主路线仍然是 Route C，而不是 A

外部评估里的三条路线里，当前 repo 采纳的路线仍然是：

- `A`：把 `schema_augmented` 做强，写成 robustness / recipe paper
- `B`：把 held-out schema transfer 写成 benchmark / measurement / evaluation paper
- `C`：坚持 `schema-reusable decision representation`，核心证据是 fixed-`d` `A->B` schema swap + `shuffle/null` controls

当前结论：

- 主路线：`C`
- fallback：`B`
- 不推荐主线：`A`

更具体地说：

- 如果后面 baseline 已经几乎填平 held-out schema gap，就及时止损 `C`，转向 `B`
- 如果 baseline gap 仍然明显，继续推进 `C`

### 3. `reuse_main` 最小版本只需要一个核心创新点

当前采纳的最小主张是：

> 学习一个固定维度、可跨 schema 复用的 decision bottleneck，使得 source schema `T_A` 下形成的 decision state，能在 target schema `T_B` 下被正确 grounding 成等价 function call。

当前明确**不采纳**“顺手再加第二个大创新点”的冲动。

当前仓库层面的解释：

- `schema token dropout`
- `name masking`
- 其它轻量 regularizer

如果未来使用，也只能是实现细节，不是第二主贡献。

## 当前采纳的关键协议约束

### 1. `A->B` 证明协议必须尽量是介入式的

当前外部评估最重要的一条补强是：

- 如果要证明的是 `decision reuse`
- 那么 `A->B` schema swap 不能退化成“又重新看一遍 query 然后重新解题”

因此当前工作判据是：

- 主证明协议里，`decoder` 应尽量只看：
  - `z`
  - `T_B`
- 不再看原始 `x`

这条要求对论文主张非常关键。

补充说明：

- 这条约束首先是**论文主证据协议**的要求；
- 是否允许另做一个 `with x` 版本作为 ceiling / 辅助 ablation，可以后面再讨论；
- 但只要主张写成 `decision reuse`，主证据不能靠 `decoder+query` 混过去。

### 2. `shuffle/null` controls 不是可选项

当前外部评估与已有本地判断完全一致：

- `true A->B`
- `shuffle d`
- `null d`

都必须存在。

否则 reviewer 很容易说：

- latent 只是压缩码
- latent 只是 canonical tool id
- decoder 实际并没有真正使用 `d`

### 3. 指标应继续坚持 AST / canonical / executable 方向

这和当前 repo 现状一致：

- 不回退到 BLEU/ROUGE
- function calling correctness 继续优先走 exact / AST / canonical 方向

当前 repo 已有的 exact evaluator 路线仍然是正确方向。

## 当前采纳的 kill / go 判据

下面这些阈值当前被采纳为**工作判据**，但要注意：

- 它们来自外部 challenge
- 不是本仓库已经被实验验证的定律
- 当前作用是帮助提前止损或推进，不是替代本地结果

### Kill 条件

如果出现下面任一类结果，当前 `decision reuse` 主 thesis 要高度警惕，甚至及时止损：

#### Kill-1：最强 baseline 的 held-out schema retention 过高

如果最强 baseline 满足：

- `Acc(A->B) / Acc(A->A) >= 0.93`
- 且 `A->A - A->B <= 3~5` 个绝对点

那么说明：

- 简单 direct recipe 已经基本解决问题
- `decision reuse` 作为主论文的空间会明显变小

#### Kill-2：最强 baseline 关闭了大部分 transfer gap

设：

- `Gap_v = Acc_v(A->A) - Acc_v(A->B)`
- `Gap_b = Acc_best(A->A) - Acc_best(A->B)`

如果：

- `(Gap_v - Gap_b) / Gap_v >= 0.8`

也就是 best baseline 关闭了 `80%` 以上的 transfer gap，

则当前解释倾向于：

- 问题更像 robustness / data engineering
- 不再像新的 decision object

#### Kill-3：controls 拉不开

如果：

- `true A->B`
- 和 `A->B_shuffle/null`

的差距不到 `10~15` 个点，

那当前不应急着写 `reuse_main` 结论。

优先解释应是：

- 协议没把想测的变量隔离出来
- 而不是“方法已经成立”

### Go 条件

如果出现下面这些结果，则应快速推进 `reuse_main`：

#### Go-1：baseline 仍有明显 transfer gap

如果：

- `vanilla` 在 `A->A` 已经不错
- 但 `A->B` 下降 `>= 12` 个点
- 且最强 baseline 仍保留 `>= 6~8` 个点 gap

则说明：

- schema transfer 不是小毛病
- 而是当前论文真正该解决的主问题

#### Go-2：held-out schema 下模型排序发生变化

如果模型在：

- `A->A`
- 和 `A->B`

上的排序发生明显变化，

则说明：

- 现有高分很可能部分依赖 schema / format alignment
- 这会增强 Route C 的说服力

#### Go-3：小 bottleneck + no-`x` 仍保留非平凡 transfer

如果在：

- 较小 `d`
- `decoder` 不看 `x`

的条件下，`A->B` 仍然保留 best baseline 的大部分性能，

那就是当前 thesis 最强的正证据。

## 和当前仓库状态的结合

基于这份外部评估，当前 repo 的工作顺序进一步收敛为：

### 阶段一：先跑完 real-data direct baseline

当前已经具备：

- `xLAM` single-answer clean slice
- `vanilla`
- `schema_augmented`
- `hammer_like`

下一步应先拿到：

- `A->A`
- `A->B`
- held-out transfer gap

再决定论文是否继续押注 `C`。

### 阶段二：只在 gap 仍明显时推进 `reuse_main`

推进前至少要满足：

- best baseline 没有把 gap 基本填平
- held-out schema 下确实存在稳定退化
- 目标 schema 自身可学

### 阶段三：若 `C` 被 kill，就转向 `B`

如果 real-data baseline 很强，当前 fallback 应是：

- 把 held-out schema transfer / schema compliance / decision competence 的分离写成 evaluation / measurement 论文

这条路更适合：

- NeurIPS Evaluations & Datasets

而不是硬写成 methods main-track。

## 当前明确不建议做的事

- 不要把 `schema_augmented` 抬成主创新
- 不要在 baseline 结果出来前重投入 `reuse_main`
- 不要把 `RL` 拉回主线
- 不要把 `execution-feedback posterior distillation` 拉回主线
- 不要把 multi-turn / live API / retrieval 一起耦合进当前主论文
- 不要把 `BFCL` 拉回默认训练主料

## 这份外部评估的当前定位

当前对 `docs/fc_pdf/function-calling-paper-evaluation.md` 的仓库内定位是：

- 它是高质量外部 challenge
- 它提供了：
  - 路线排序
  - 最小方法接口建议
  - kill/go 判据
- 但它**不是**：
  - 本地实验结果
  - 可直接替代 repo 内实现与验证的证据

## 一句话结论

当前最合理的推进不是继续抛光 `schema_augmented`，而是：

**先用 xLAM real-data baseline 把 held-out schema gap 跑出来，再用这份外部评估给出的 kill/go 判据决定 Route C 是否值得继续。**
