# 2026-04-14 xLAM Function Calling 60k 接入审计

## 背景

当前论文主线已经明确：

- `BFCL` 更适合作为 benchmark / eval
- baseline 训练源应优先使用社区常见的 function-calling training dataset

因此今天开始把 `Salesforce/xlam-function-calling-60k` 接进当前仓库，作为新的 baseline 正例训练源候选。

## 今天确认下来的官方信息

基于官方仓库、官方数据卡下游说明和官方生态文档，当前可以确认：

- 数据集名称：
  - `Salesforce/xlam-function-calling-60k`
- 常见字段：
  - `id`
  - `query`
  - `tools`
  - `answers`
- `tools` 与 `answers` 这两个字段在很多消费侧会以字符串形式存储 JSON
- `answers[*].arguments` 在部分下游用法里也会是序列化 JSON 字符串，需要额外 `json.loads`

license 相关信息：

- `xLAM` 官方仓库代码：`Apache 2.0`
- `xLAM` 数据：`CC-BY-NC-4.0`
- 数据定位：
  - research only

## 当前仓库里已经新增的接入骨架

新增文件：

- `src/schema_reuse/data/xlam_official.py`
- `scripts/build_xlam_fc_single_call_slice.py`
- `configs/xlam_fc_single_call/data.json`
- `tests/data/test_xlam_official.py`

当前接入范围刻意收窄为：

- 只处理单轮正例 function-calling 数据
- 允许一个样本有多个候选工具
- 但当前 slice 只接受：
  - `answers` 里恰好一个 tool call 的样本

输出目标仍对齐当前统一 candidate 格式：

- `user`
- `ground_truth`
- `tool_spec`
- `tool_pool_spec`
- `metadata`
- `source_benchmark`

## 真实本地全量文件审计

当前实际使用的本地原始文件：

- `/root/autodl-fs/tooluse-artifacts/external/xlam/xlam_function_calling_60k.json`

真实文件结构确认如下：

- 顶层 payload 是 `list`
- 总样本数：`60000`
- `id` 全部是整数，不是字符串
- `tools` 字段全部是字符串化 JSON
- `answers` 字段全部是字符串化 JSON

`answers` 的 call 数分布：

- `1 call`：`28461`
- `2 calls`：`25422`
- `3 calls`：`4697`
- `4 calls`：`1056`
- 更高 call 数仍然存在，但占比更低

这说明：

- xLAM 的多答案 / 多 call 不是脏数据，而是数据设计的一部分
- 当前仓库把它收窄成 single-answer clean slice，是为了先完成第一版 real-data baseline 主线

## 当前实现策略

### 1. 不直接把 Hugging Face 在线下载写死进主脚本

原因：

- 当前机器到 Hugging Face 连接不稳定
- repo 需要支持无 Codex、自助式恢复
- 用本地输入路径更容易跨机器复用

所以当前配置采用：

- `input_path = $XLAM_FC_ROOT/xlam_function_calling_60k.json`

也就是说：

- 先把原始数据导出到本地
- 再由仓库脚本统一 ingest

### 2. 先做单-call 正例 slice，不把 no-call / multi-turn 一起耦合

原因：

- 当前主线先需要一个真实 baseline 正例训练源
- `When2Call` / irrelevance / no-call 是下一层问题，不该在 ingest 第一步就耦合进去
- multi-turn function calling 当前也不是论文主线

### 3. tool schema 在 ingest 阶段就归一化成 richer JSON Schema 近似结构

当前做法：

- 把 `parameters` 从 xLAM 原始字段归一化成：
  - `type=object`
  - `properties`
  - `required`

这样后续：

- paired transform
- LLaMA-Factory export
- exact evaluator

都可以继续复用现有 richer schema 路径。

## 真实全量接入时新增的一个兼容修复

真实数据第一次跑时暴露出的唯一实现问题是：

- 当前代码假设 `id` 是字符串
- 真实 xLAM 全部是整数型 `id`

因此当前仓库补了一个极窄修复：

- 数值型 `id` 现在会被统一转成字符串 `sample_id`
- 没有顺手扩成 multi-call 主线

对应测试已经补到：

- `tests/data/test_xlam_official.py`

## 今天已经完成的事

今天完成的是：

- 官方字段与 license 审计
- 本地 ingest 骨架
- 合成 fixture 测试
- 对真实全量 `xLAM` 数据跑通 ingest
- 对真实全量 `xLAM` 数据跑通 paired dataset
- 对真实全量 `xLAM` 数据跑通 `LLaMA-Factory` baseline 导出
- 为首批 real-data baseline 准备好 `pilot1000` 配置

## 已通过的本地验证

当前新增测试：

- `tests/data/test_xlam_official.py`

覆盖内容：

- 字符串化 `tools/answers` 的解析
- `arguments` 的二次 JSON 解析
- richer schema 的 `required` 归一化
- single-call slice 的过滤逻辑
- 整数型 `id` 到字符串 `sample_id` 的兼容

当前整仓测试结果：

- `/root/miniconda3/envs/tooluse-llf/bin/python -m pytest -q`
- 结果：`29 passed`

## 真实全量运行结果

ingest 命令：

```bash
XLAM_FC_ROOT=/root/autodl-fs/tooluse-artifacts/external/xlam \
  /root/miniconda3/envs/tooluse-llf/bin/python scripts/build_xlam_fc_single_call_slice.py \
  --config configs/xlam_fc_single_call/data.json
```

结果：

- raw `60000`
- accepted `25711`
- rejected `34289`
- rejection reasons：
  - `not_single_answer=31539`
  - `mentions_schema_surface_forms=2750`
- unique tools：`2475`
- unique split groups：`24206`

paired dataset 结果：

- `train=20588`
- `dev=2553`
- `test=2570`

导出后的 `LLaMA-Factory` 数据集记录数：

- `xlam_fc_single_call_vanilla_train=20588`
- `xlam_fc_single_call_vanilla_eval=2553`
- `xlam_fc_single_call_vanilla_test=2570`
- `xlam_fc_single_call_schema_augmented_train=41176`
- `xlam_fc_single_call_schema_augmented_eval=5106`
- `xlam_fc_single_call_schema_augmented_test=5140`
- `xlam_fc_single_call_hammer_like_train=41176`
- `xlam_fc_single_call_hammer_like_eval=5106`
- `xlam_fc_single_call_hammer_like_test=5140`

## 首批 real-data baseline 配置

当前已经补好的本机 pilot 配置：

- `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_vanilla_qlora_pilot1000.yaml`
- `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_schema_augmented_qlora_pilot1000.yaml`
- `configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_hammer_like_qlora_pilot1000.yaml`

当前选择 `pilot1000` 而不是直接跑完整多 epoch，原因是：

- `2080 Ti 22GB` 更适合先做真实数据 bring-up
- 需要先尽快得到第一批 real-data direct baseline 结果
- 完整预算应等第一批结果出来后再决定

## 下一步

1. 真实本地原始数据文件已经到位：
   - `/root/autodl-fs/tooluse-artifacts/external/xlam/xlam_function_calling_60k.json`
2. ingest 已完成：

```bash
/root/miniconda3/envs/tooluse-llf/bin/python scripts/build_xlam_fc_single_call_slice.py \
  --config configs/xlam_fc_single_call/data.json
```

3. paired dataset 已完成：

```bash
/root/miniconda3/envs/tooluse-llf/bin/python scripts/build_paired_dataset.py \
  --config configs/xlam_fc_single_call/data.json
```

4. baseline 导出已完成：

```bash
/root/miniconda3/envs/tooluse-llf/bin/python scripts/export_llamafactory_baselines.py \
  --processed-dir data/processed/xlam_fc_single_call \
  --output-dir data/llamafactory/xlam_fc_single_call \
  --dataset-prefix xlam_fc_single_call
```

5. 当前下一步是跑真实 baseline 训练，并把轻量结果证据同步回仓库 `results/`

## 当前结论

`xLAM` 现在已经不是“纸面上的候选训练源”。

它在当前仓库里已经具备：

- 明确的官方字段假设
- 可测试的 ingest 模块
- 可执行的本地 slice 构建脚本

它现在已经是：

- 已完成真实全量接入
- 已完成 paired-schema 切分
- 已完成 `LLaMA-Factory` baseline 导出

但它**还不是**已经完成真实 baseline 结果验证的论文证据，因为：

- real-data baseline run 还没全部产出
- held-out schema transfer 的 direct baseline 结论还没出来
