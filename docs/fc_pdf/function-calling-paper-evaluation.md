# Function-Calling Paper Evaluation

- Share URL: https://chatgpt.com/share/69ddda2b-6c78-8323-8645-918d5adbe538
- Source title: Function-Calling Paper Evaluation
- Note: inline ChatGPT share citations were normalized to `[Ref n]`. Reference links below were reconstructed from the same share-page payload; a few multi-source groups are best-effort reconstructions.

## Result

## 最终结论

**不能。仅靠 `schema_augmented`，不够支撑 NeurIPS 2026 主会主论文。**  
它最多能撑起一个**robustness / recipe / data-centric**方向的论文，不是你现在想要的那个“新的 scientific object”。**我推荐主路线是 C；B 是很强的 fallback，但更像 NeurIPS 2026 Evaluations & Datasets track；A 不建议继续当主线。** 2025–2026 这条线已经有很强的 recipe 型工作：Hammer 直接打 naming-convention overfit，用 augmented data + function masking；EMNLP 2025 的 ToolGT/Guided-Structured Templates 把 structured prompting + finetuning 做成完整范式；2026 的 Trace-Free+ 又把 tool description / parameter schema repair 做成了“interface optimization for unseen tools”的一条线。继续把 `schema_augmented` 做强，审稿人会自然把你归到这一类。[Ref 1]

## 3 条最核心理由

**第一，`schema_augmented` 不是新的 scientific object。**  
它没有改变研究对象，还是在做 `p(y | x, T)`，只是把 `T` 的表面形式扩充、改写、mask、扰动而已。这个范式在最近文献里已经非常拥挤：Hammer 是 robustness + masking，ToolGT 是 prompting / finetuning scaffold，Trace-Free+ 是 interface rewriting / schema repair。你如果没有一个**显式可检验的“schema-reusable decision state”**，那它就是 baseline recipe，不是新对象。[Ref 2]

**第二，现在真正有意思的问题，已经不是“能不能输出对的 JSON”，而是“latent decision competence 和 interface compliance 能不能分开”。**  
HammerBench 直接指出，**parameter-name errors** 是 function-calling 失败的重要来源；BFCL 之所以强调 AST 级评测，也是在避免把格式字符串当成全部；一个 2026 诊断研究甚至明确指出，某些 agent/tool-use 高分很大程度来自**和评测 schema 的 format alignment**，而不是更强的潜在能力。你的 thesis 正好卡在这个缝里：要证明的是 **decision reuse**，不是 formatting。[Ref 3]

**第三，NeurIPS 2026 已经把 evaluation 本身抬成了 scientific object。**  
官方新设的 E&D track 明确欢迎：benchmark overfitting、failure-mode analysis、stress-testing、evaluation design comparison、negative results。也就是说，**如果你不做 route C 的方法学主张，只做 held-out schema transfer 评测，本身是成立的，但更像 E&D，不像主会方法论文。** 主会当然也欢迎“对现有方法做新 insight 的深入分析”，但那条路的最优 framing 仍然不是 recipe，而是 representation/generalization。[Ref 4]

---

## 直接回答 1 / 2：`schema_augmented` 到底够不够

**不够。**

它更像下面这几类里的组合，而**不是**新的 scientific object：

- **baseline recipe**：训练时把 schema 做 paraphrase / rename / reorder / distractor augmentation。
- **robustness trick**：让模型少依赖 function/arg names，多依赖 descriptions。
- **data engineering**：扩大表面覆盖率，减少 lexical shortcut。
- **prompting / masking variant**：如果你在推理时也做 schema normalization、name masking、description rewriting，那更明显。

它**不是** scientific object 的原因很简单：  
你没有提出一个新的、可 falsify 的被研究变量。  
真正的新对象应该像这样表述：

> 是否存在一个**紧凑、可跨 schema 复用的 decision state**，它保留“该调用什么功能、各参数该绑定什么值”的语义，却不依赖具体 schema wording？

只要论文还停留在“多见一点 schema 变体就会更鲁棒”，它就不是这个对象。

---

## 三条路线的判断

### 路线 A：把 `schema_augmented` 做强，写成 robustness / recipe paper

**新颖性上限：低。**  
2025–2026 已经有 Hammer、ToolGT、Trace-Free+ 这种相邻路线。你再做一个更强 augmentation，很容易被审稿人读成“another good recipe”。[Ref 1]

**最大风险：**  
增益存在，但解释权不在你。审稿人会说：
1. 这只是更好的 data coverage；  
2. 这只是 interface normalization；  
3. 这不是 decision reuse，只是让测试分布更像训练分布。

**最适合的投稿口味：**  
ACL/EMNLP Findings、industry/system paper、或者一个 practical recipe paper。

**是否适合 NeurIPS 2026 主会：**  
**不适合。**

---

### 路线 B：做 benchmark / measurement / evaluation paper，核心是 held-out schema transfer

**新颖性上限：中到中高。**  
如果你能证明：**现有 leaderboards 部分在测 schema alignment，而不是 latent decision competence**，并且 held-out schema transfer 会**改变模型排序或结论**，这就是一篇很像样的 evaluation paper。NeurIPS 2026 E&D 官方 scope 正欢迎这种工作。[Ref 5]

**最大风险：**  
被说成“another stress test”或“synthetic schema paraphrase benchmark”。尤其如果你的 `T_B` 只是名字改写、没有强 controls，这条路会很虚。

**最适合的投稿口味：**  
**NeurIPS 2026 E&D track**。这是它最自然的位置。[Ref 5]

**是否适合 NeurIPS 2026 主会：**  
**通常不适合主会，适合 E&D。**  
除非你能证明 held-out schema transfer 明显推翻现有 benchmark 结论。

---

### 路线 C：坚持 schema-reusable decision representation；核心证据是 fixed-d A→B swap + shuffle/null controls

**新颖性上限：高。**  
这是唯一一条能把论文从“recipe/eval”推到“representation/generalization hypothesis”的路。它正好回应近两年的核心张力：function-calling 的高分到底是 latent capability，还是 interface compliance。Hammer 的 naming-overfit、HammerBench 的 parameter-name failures、ReLE 的 format alignment 都在给这条路铺垫。[Ref 6]

**最大风险：**  
如果 baseline 已经把 held-out schema gap 基本填平了，那你这个 thesis 直接没空间。第二个风险是 protocol 不够硬：如果 decoder 还能看原 query，或者 B/shuffle/null 分不出层次，审稿人会说你没有证明 reuse，只是又解了一遍题。

**最适合的投稿口味：**  
**NeurIPS / ICLR / ICML main-track 的 representation/generalization 口味。**

**是否适合 NeurIPS 2026 主会：**  
**适合，而且这是唯一我会认真押注主会的路线。**

---

## 推荐主路线 / 不推荐路线

**推荐主路线：C。**  
**不推荐路线：A。**  
**B 只作为 C 做不出来时的高质量 fallback，且优先投 NeurIPS E&D，不要硬往 main track 塞。**

---

## 如果走 C：最小可成立版本是什么

### 需要第二个创新点吗？

**不需要。一个核心创新点 + 强协议/强证据，够。**

这个核心创新点就是：

> **学习一个 fixed-dimensional、schema-reusable 的 decision bottleneck，使得在 source schema `T_A` 下形成的 decision state，能在不重新看原 query 的情况下，被 target schema `T_B` 正确解码成等价 function call。**

这已经是完整主张了。  
第二个“创新点”只会稀释故事。你最多加一个很轻的 regularizer，比如 schema token dropout / name masking，但**只能当实现细节，不能当第二主贡献。**

### 最小方法接口

最小接口应该长这样：

\[
z = E_\theta(x, T_A), \quad z \in \mathbb{R}^d
\]

\[
\hat y_B = D_\phi(z, T_B)
\]

训练时用 paired equivalent schemas：

\[
(x, T_A, y_A, T_B, y_B)
\]

最小 loss：

\[
L = L_{\text{self}}(A\to A) + L_{\text{self}}(B\to B) + \lambda L_{\text{swap}}(A\to B, B\to A)
\]

其中最关键的是：

**在 swap 评测时，decoder 不允许再看原 query `x`。**  
否则你证明不了 “reuse”，只能证明 “重新解题”。

再强调一次：  
**decoder 只看 `z + T_B`，不看 `x`。**  
这是 route C 能不能站住的生死线。

### 最关键的 3 个判决实验

**实验 1：A→A vs A→B held-out schema transfer（主实验）**  
同一语义任务，训练时只见 `T_A`，测试时换成未见过表面的 `T_B`。  
比较 `vanilla / schema_augmented / hammer_like / reuse_main`。  
主指标不要用 raw JSON string EM，用 **BFCL-style 的 AST/canonical executable accuracy**，再加 tool selection / slot-value accuracy。因为你的论文不是在测字符串格式。[Ref 7]

**实验 2：swap 的 positive / shuffle / null controls（证伪实验）**  
给定同一个 `z_A`：
- `+control`: decode with true `T_B`
- `shuffle control`: 打乱 B 中 function/arg 语义映射，但匹配词长、arity、tool 数量
- `null control`: 换成无关 schema `T_{\varnothing}`，统计量匹配但语义不对应

你要看到：  
`A→B` 明显高，`A→B_shuffle / A→B_null` 明显低。  
否则就说明 z 不是 reusable decision state，或者你的 B 根本不够 hard。

**实验 3：information-budget ablation（固定 d + no-x 的必要性）**  
至少做两个 ablation：
- vary `d`
- decoder 是否能看 `x`

你需要证明：
1. 在**不看 x**时，仍有非平凡 A→B transfer；  
2. 这个 transfer 在较小 `d` 下仍成立；  
3. 一旦放开 `x` 或放开 free-form latent，结果虽可能更高，但就不再能支撑 “decision reuse” 的主张。

---

## 哪些东西绝对不要拉回主线

**不要拉 RL。**  
最近 RL / GRPO / verifier 这条线已经会把故事改写成 policy optimization，不再是 representation hypothesis。[Ref 8]

**不要拉 execution feedback posterior distillation。**  
这会把论文变成 training pipeline paper。

**不要拉 multi-turn / long-horizon / live API / retrieval。**  
这一块近两年已经有 NESTful、HammerBench、FuncBenchGen、Live API Bench 在打，而且它们关注的是 sequencing、state tracking、live execution robustness，不是 schema-reuse。把这些拉进来只会让你的因果识别变差。[Ref 9]

**不要把 BFCL 拉回训练主料。**  
BFCL 应该继续做外部 eval；你如果拿它进训练，会立刻重新引入 benchmark/schema alignment confound。BFCL 本身就是为了评测而生的。[Ref 7]

**不要做 free-form rationale latent。**  
那会被读成 another prompting variant，不是 fixed-d decision object。

---

## 最小实验矩阵

我建议你把矩阵压到下面这一版，够用了：

**模型：**
- vanilla
- schema_augmented
- hammer_like
- reuse_main

**训练数据：**
- 只用你现在 xLAM clean slice 主体
- 对 `schema_augmented` / `hammer_like` / `reuse_main` 使用同一套 A/B paired schema source，保证公平

**评测条件：**
- `A→A` IID
- `A→B` held-out schema transfer
- `A→B+distractor/order-shift`
- `A→B_shuffle`
- `A→B_null`

**主指标：**
- canonical / AST / executable accuracy
- tool selection accuracy
- slot-value exact/F1
- transfer retention = `Acc(A→B) / Acc(A→A)`

**只给 reuse_main 额外做：**
- `d ∈ {small, medium, larger}` ablation
- decoder with/without `x`

这就是最小可投矩阵。

---

## go / no-go 判据

### 什么结果说明 decision-reuse thesis 不值得继续

我给你非常直接的 kill criteria：

**Kill-1：best baseline 的 held-out schema retention 太高。**  
如果最强 baseline（大概率是 `schema_augmented` 或 `hammer_like`）满足：

- `Acc(A→B) / Acc(A→A) >= 0.93`
- 且 `A→A - A→B <= 3~5` 个绝对点

那就说明 **simple robustness/data engineering 已经基本解决问题**。  
这时 route C 不值得做成主线。

**Kill-2：schema_augmented 已经关闭了大部分 vanilla gap。**  
设
- `Gap_v = Acc_v(A→A) - Acc_v(A→B)`
- `Gap_b = Acc_best(A→A) - Acc_best(A→B)`

如果

\[
(Gap_v - Gap_b)/Gap_v \ge 0.8
\]

也就是 best baseline 关闭了 **80% 以上** 的 transfer gap，  
那我会判 **decision reuse thesis 基本失去必要性**。

**Kill-3：controls 分不出层次。**  
如果 true `A→B` 和 `A→B_shuffle/null` 的差距不到 **10–15 个点**，  
先别做 reuse_main。不是 thesis 死了，是你的 protocol 没隔离出你想测的东西。

### 什么结果说明应该马上做 reuse_main

**Go-1：baseline 有明显 transfer gap。**  
如果 vanilla 在 `A→A` 已经不错，但 `A→B` 掉 **>= 12 个点**，而最强 baseline 仍然保留 **>= 6–8 个点** gap，  
说明**schema transfer 不是小毛病，是主问题**。

**Go-2：ranking 在 held-out schema 下改变。**  
如果某些 agent-tuned / benchmark-tuned 模型在 `A→A` 很强，但 `A→B` 明显失速，甚至被更一般的模型反超，  
这就是典型的 schema/format alignment 信号。这个现象和最近评测里的 format-alignment 观察是同向的。[Ref 10]

**Go-3：一个小 bottleneck 仍保留非平凡 transfer。**  
如果你试一个非常小的 `d`，在 decoder 不看 `x` 的条件下，`A→B` 还能保留 best baseline 大部分性能，  
那就是最强证据：**compact reusable decision object 可能真的存在。**

---

## 我会怎么下最后 verdict

**最终结论：**  
- **`schema_augmented` 单独成文，不够 NeurIPS 2026 主会。**
- **推荐主路线：C。**
- **不推荐路线：A。**
- **B 是高质量 fallback，但应该按 NeurIPS 2026 E&D 来写，不要伪装成 main-track 方法论文。**

**一句话版：**  
你现在最该做的不是把 `schema_augmented` 再抛光，而是先用一个**极硬的 held-out schema swap protocol** 判定：  
**当前高分到底是 decision competence，还是 schema compliance。**  
如果 baseline 已经几乎无 gap，就 kill C；  
如果 gap 明显且 controls 站得住，就立刻做 `reuse_main`，并且只做 **一个核心 bottleneck 创新点**。

## References

### Ref 1
- https://openreview.net/forum?id=yVQcr4qjD6
- https://aclanthology.org/2025.emnlp-main.1242.pdf
- https://arxiv.org/html/2602.20426
- Original token: `citeturn563568view0turn273946view0turn531400view1`

### Ref 2
- https://openreview.net/forum?id=yVQcr4qjD6
- https://aclanthology.org/2025.emnlp-main.1242.pdf
- https://arxiv.org/html/2602.20426
- Original token: `citeturn563568view0turn273946view0turn531400view2`

### Ref 3
- https://aclanthology.org/2025.findings-acl.175/
- https://proceedings.mlr.press/v267/patil25a.html
- https://arxiv.org/pdf/2601.17399
- Original token: `citeturn192454view2turn339113view4turn759234view0`

### Ref 4
- https://neurips.cc/Conferences/2026/CallForEvaluationsDatasets
- https://neurips.cc/Conferences/2026/CallForPapers
- Original token: `citeturn394997view0turn394997view1`

### Ref 5
- https://neurips.cc/Conferences/2026/CallForEvaluationsDatasets
- Original token: `citeturn394997view0`

### Ref 6
- https://openreview.net/forum?id=yVQcr4qjD6
- https://aclanthology.org/2025.findings-acl.175/
- https://arxiv.org/pdf/2601.17399
- Original token: `citeturn563568view0turn192454view2turn759234view0`

### Ref 7
- https://proceedings.mlr.press/v267/patil25a.html
- Original token: `citeturn339113view4`

### Ref 8
- https://arxiv.org/html/2604.05387v1
- Original token: `citeturn424370view0`

### Ref 9
- https://aclanthology.org/2025.emnlp-main.1702.pdf
- Original token: `citeturn759234view3turn192454view1turn338888view0turn784773view0`

### Ref 10
- https://arxiv.org/pdf/2601.17399
- Original token: `citeturn759234view0`

## Deduplicated Links

- https://openreview.net/forum?id=yVQcr4qjD6
- https://aclanthology.org/2025.emnlp-main.1242.pdf
- https://arxiv.org/html/2602.20426
- https://aclanthology.org/2025.findings-acl.175/
- https://proceedings.mlr.press/v267/patil25a.html
- https://arxiv.org/pdf/2601.17399
- https://neurips.cc/Conferences/2026/CallForEvaluationsDatasets
- https://neurips.cc/Conferences/2026/CallForPapers
- https://arxiv.org/html/2604.05387v1
- https://aclanthology.org/2025.emnlp-main.1702.pdf
