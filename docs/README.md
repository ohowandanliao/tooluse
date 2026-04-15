# 文档总览

## 固定阅读路径

第一次进入仓库，按这个顺序读：

1. `../README.md`
   - 项目目标、快速开始、仓库结构
2. `../RULES.md`
   - 用户可直接修改的规则入口
3. `PROJECT_RULES.md`
   - 工程细则、文档规范、产物规范
4. `../STATUS.md`
   - 当前真实状态、已验证路径、下一步建议
5. `../HANDOFF.md`
   - 新会话最短接手路径
6. `new-machine-quickstart.md`
   - 新机器恢复、多机实验分工、主实验与补充实验矩阵
7. `../results/README.md`
   - 仓库内实验结果证据入口
8. `../2026-03-31-nips2026-function-calling-idea-draft-v2.md`
   - 当前论文主草稿

## 文档分层

### 入口与治理

- `../README.md`
  - 面向仓库访问者的总入口
- `../RULES.md`
  - 用户维护的规则入口，优先级高于其它说明文档
- `PROJECT_RULES.md`
  - 工程与文档维护细则
- `../STATUS.md`
  - 当前状态
- `../HANDOFF.md`
  - 接手说明

### 研究与运行

- `llamafactory-baseline.md`
  - baseline runtime 与 exact evaluator 使用说明
- `new-machine-quickstart.md`
  - 新机器最短安装与开跑路径，以及多机实验分工、baseline/补充实验矩阵、标准回传物
- `environment-repro.md`
  - 新机器环境恢复、裸 Linux 安装脚本、镜像/快照策略
- `../results/README.md`
  - 仓库内实验结果证据入口
- `../results/local_2080ti/pilot_v1/README.md`
  - 当前已提交的本机 run 结果摘要
- `records/2026-04-12-local-2080ti-qlora-bringup.md`
  - 本机 `2080 Ti` 上的 `LLaMA-Factory` 打通记录
- `records/2026-04-13-bfcl-usage-and-baseline-data-audit.md`
  - BFCL 的外部用法审计，以及可替代的 baseline 数据源判断
- `records/2026-04-14-xlam-fc60k-ingest-audit.md`
  - `xLAM function-calling-60k` 的字段、license、真实全量 ingest 结果与当前边界
- `records/2026-04-14-external-paper-eval-synthesis.md`
  - 外部 `GPT-5.4-pro` 论文评估结果的仓库内整合版，以及当前采纳的 kill/go 判据
- `records/pilot-v1-resource-estimate.md`
  - 算力和服务器需求估计

## 维护约定

- 用户原则统一写在 `../RULES.md`。
- 工程细则、文档分层和产物规范统一写在 `PROJECT_RULES.md`。
- 影响当前决策的文档保留在根目录或活跃 `docs/` 目录。
- 只对内部协作、AI 会话或历史草稿有意义的文档，不默认保留到 release 仓库。
- 环境、checkpoint、editable 第三方源码和其它重型产物不要放进仓库根目录。
- 轻量实验结果证据统一放在 `../results/`。
