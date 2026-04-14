# 2026-04-14 论文进度判断与下一步路线

## 当前阶段判断

截至今天，这个项目已经完成的是：

- baseline 工程链路打通：
  - `build -> paired dataset -> LLaMA-Factory export -> train -> predict -> exact eval`
- 本机单卡 `2080 Ti 22GB` 的 QLoRA bring-up 已验证
- `BFCL v4` 官方数据的一条单轮单工具 ingest / audit / export 路径已接通
- 轻量实验结果证据已经可以回收到仓库 `results/`

但这离论文当前 `v2` 草稿要求的证据链，仍然差一大截。

更准确地说，项目现在还处在：

- **baseline runtime ready**
- **paper evidence not ready**

而不是：

- “已经开始做主实验矩阵”

## 为什么现在还不能说论文进入主实验阶段

### 1. `pilot_v1` 仍然只是 smoke 数据

`pilot_v1` 当前能证明的是：

- runtime 没坏
- exact evaluator 没坏
- toy 变换链路没坏

它不能证明的是：

- `A->B` reuse 是否成立
- direct baseline 在真实 held-out schema 上到底有多脆弱
- schema augmentation / hammer-like recipe 与未来方法侧是否存在真正可判决的差距

### 2. 当前方法主线还没有进入“可判决”状态

论文草稿要求的表 R 需要：

- `A->A`
- `B->B`
- `A->B`
- `shuffle d`
- `null d`

但仓库当前实际上还没有：

- `reuse_main` 的真实训练实现
- fixed-`d` `A->B` 推理接口
- `shuffle/null` 的真实 counterfactual decode 管线

目前的 `scripts/eval_counterfactual.py` 还是 stub，只能写空 report；这说明方法主线还没有真正进入 pilot。

### 3. 训练源与 benchmark 的角色刚刚厘清，还没有落成新数据主线

昨天已经确认：

- `BFCL` 更适合 benchmark / eval
- baseline 训练源更应该优先接 function-calling training dataset

但这个判断还没有完全落地成新主线，因为：

- `xLAM/APIGen` 当时还没正式接入仓库流水线
- semantic-task-aware split、paired transform、held-out alias / transform seed 这些关键实验条件还没落地到真实训练数据上

2026-04-14 当天晚些时候，这里的第一个缺口已经补上：

- `xLAM function-calling-60k` 的 single-answer clean slice 已在本机真实全量数据上完成 ingest / paired / export
- 当前 clean slice 规模：
  - `train=20588`
  - `dev=2553`
  - `test=2570`
- 因此阶段一现在不再是“接入 xLAM”，而是“把 xLAM 上的 real-data direct baseline 跑出来”

## 结合既有外部深研后的额外收紧

这一步不是新增方向，而是把当前路线进一步收紧。

结合已有外部深研，可以额外确认三件事：

### 1. `EFPD` 现在不能回到主叙事

外部审阅对 `EFPD` 的批评点非常集中：

- same-budget 很难真正写公平
- 很容易被看成 `token-level hindsight` 的换空间版本
- baseline 对照、统计显著性、teacher leakage 都很容易被 reviewer 抓住

这和当前仓库里的 `v2` 收窄方向是一致的。

所以当前正确做法不是“先做 decision reuse，再顺便把 EFPD 也讲进去”，而是：

- **先证明 decision reuse 是否存在**
- `EFPD` 暂时只保留为未来 phase，不回到当前主实验主线

### 2. counterfactual decoding 必须是介入式协议，不是观察性指标

外部深研对这点说得非常明确：

- latent consistency / clustering 这类指标不够硬
- reviewer 会直接怀疑 latent 只是压缩码、canonical tool id 或 decoder 没有真正使用 `d`

因此，真正能支撑当前主 thesis 的，不是“看起来稳定”的表征指标，而是：

- fixed-`d` 的 schema-swap
- `shuffle d`
- `null d`
- `CF-Gap`

这也意味着当前仓库里的 `scripts/eval_counterfactual.py` 只是占位，还远远不够支撑论文主证据。

### 3. 如果 direct baseline 已经解决问题，方法主线要及时止损

外部深研反复强调一个 reviewer 视角：

- 如果最后结论只是“rename augmentation / masking / prompt recipe 会更稳”
- 或者 `schema_augmented` / `Hammer-style` 已经把 held-out schema 泛化基本做掉

那论文会更像 robustness / recipe engineering，而不是新的 decision object。

这进一步强化了当前推进顺序：

- 先拿真实数据把 direct baseline 的真实上限和真实缺口跑出来
- 再决定 `reuse_main` 是否值得实现

## 结论：现在最合理的推进顺序

论文推进应该拆成三个阶段，而不是同时推所有方向。

## 阶段一：先把真实 baseline 数据主线建起来

这一步的目标不是创新，而是把论文主实验前的地基补齐。

第一优先级应是：

- 接 `Salesforce/xlam-function-calling-60k`

原因：

- 外部实践里它更像标准训练源，而不是 benchmark
- 和当前单轮 function-calling baseline 最贴近
- 比直接把 `BFCL possible_answer` 压成单一监督 target 更干净

这一阶段要完成的最小闭环：

1. 审计 `xLAM` 的字段、license、样本格式
2. 明确单轮样本如何映射到当前 repo 的统一字段：
   - `user`
   - `tool schema`
   - `ground truth call`
3. 做 semantic-task-aware split
4. 在 split 内生成 paired schemas：
   - `rename_only`
   - `rename+arg`
   - `rename+arg+reorder`
5. 增加 surface-form leakage 审计：
   - 用户文本里显式出现 tool / arg 名称的样本，要过滤或一致替换

这一阶段的产出应该是：

- 一个真实可训练的数据主线
- 一个真实可做 held-out schema generalization 的基线矩阵入口

## 阶段二：先做表 P，不要急着做表 R

在方法主线缺位的情况下，先做表 R 没有意义，因为当前并没有真实的 fixed-`d` 接口。

所以更合理的顺序是：

- 先用真实数据跑 direct baseline，做表 P 所需的 held-out target schema 泛化结果

优先比较：

- `vanilla`
- `schema_augmented`
- `hammer_like`

要回答的问题是：

- 真实 held-out schema transfer 到底有多难？
- `schema_augmented` 和 `hammer_like` 在真实数据上会不会已经把问题基本解决？

如果 direct baseline 已经在 held-out B 上很好，那论文主张的空间会明显变小，应该尽早知道，而不是先写方法。

这一阶段至少要补齐：

- real-data 的 `B->B` / held-out-B 评测
- transform family 分组结果
- `3` 个随机种子
- `results/` 下的证据包与命令记录

## 阶段三：只有在 direct baseline 没解决问题时，才做 `reuse_main`

只有同时满足下面两点，方法主线才值得继续：

1. 真实数据上的 held-out schema transfer 确实存在稳定退化
2. 目标 schema 的 `B->B` 自身是可学的

只有在这种前提下，`reuse_main` 才有判决空间。

到那时，最小方法实现也必须非常克制，只做论文草稿要求的最小闭环：

- `A` 侧编码
- fixed-`d` `A->B` grounding
- `shuffle/null` 控制
- 与 matched bottleneck / latent-consistency-only 对照

不要在这一步提前捞回：

- `RL`
- posterior distillation
- multi-turn
- rerank

## 当前最该做的具体事情

如果只选一个“下一步马上开工”的任务，应该是：

**在已经接通的 `xLAM/APIGen` baseline 主线上跑出第一批 real-data direct baseline。**

不是先做：

- `reuse_main`
- `BFCL train`
- `ToolACE`
- `RL`
- 多轮长轨迹

原因很简单：

- 不先把真实 baseline 数据主线建好，后面的所有方法实验都没有可判决的地基。

## 对论文成败最关键的几个门槛

当前真正的 go / no-go 顺序应该是：

1. `xLAM` 能不能干净接入并生成 audit-aware paired schemas？
2. 在真实 held-out schema 上，direct baseline 是否确实会明显退化？
3. `B->B` ceiling 是否足够可解释？
4. 只有前三项成立，`reuse_main` 才值得实现

如果第 2 步就发现：

- `schema_augmented` 或 `hammer_like` 已经足够强

那这篇论文就要尽早面对一个现实：

- 现在的 `decision reuse` 主 thesis 可能没有足够硬的实验空间

## 当前明确不建议做的事

- 不要把 `pilot_v1` 结果继续扩写成“方法失败”或“方法有希望”
- 不要把 `BFCL` 直接升级成默认训练主料
- 不要在 real-data baseline 还没跑出来前就写 `reuse_main`
- 不要在主命题还没站住前把 `RL`、posterior distillation、多轮 tool-use 捞回主线

## 一句话总结

当前项目最缺的不是再多一个方法模块，而是：

**先把真实训练源、真实 held-out schema baseline、真实判决协议补成闭环。**
