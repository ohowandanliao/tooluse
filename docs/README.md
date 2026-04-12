# 文档总览

## 固定阅读路径

第一次进入仓库，按这个顺序读：

1. `../README.md`
   - 项目目标、快速开始、仓库结构
2. `PROJECT_RULES.md`
   - 三条原则、文档规范、产物规范
3. `../STATUS.md`
   - 当前真实状态、已验证路径、下一步建议
4. `../HANDOFF.md`
   - 新会话最短接手路径
5. `../2026-03-31-nips2026-function-calling-idea-draft-v2.md`
   - 当前论文主草稿

## 文档分层

### 入口与治理

- `../README.md`
  - 面向仓库访问者的总入口
- `PROJECT_RULES.md`
  - 项目原则和文档维护规则的单点来源
- `../STATUS.md`
  - 当前状态
- `../HANDOFF.md`
  - 接手说明

### 研究与运行

- `llamafactory-baseline.md`
  - baseline runtime 与 exact evaluator 使用说明
- `records/2026-04-12-local-2080ti-qlora-bringup.md`
  - 本机 `2080 Ti` 上的 `LLaMA-Factory` 打通记录
- `records/deepresearch-status.md`
  - 研究审计日志与判断依据
- `records/pilot-v1-resource-estimate.md`
  - 算力和服务器需求估计
- `superpowers/plans/2026-04-08-schema-reuse-pilot-v1-implementation-plan.md`
  - `pilot_v1` 的历史实现计划，可能提到已删除的手写 trainer 路径

### 提示词资产

- `prompts/gpt54-pro-prompt-pilot-audit.md`
  - 严格审计 `pilot` 方案的提示词
- `prompts/deepresearch-prompt-2-feedback-budget-teacher-leakage.md`
  - 历史审计提示词，不属于当前主线

### 归档

- `archive/drafts/`
  - 已被替代的旧草稿
- `archive/reviews/`
  - PDF 审稿意见、外部总结、审计报告
- `archive/share-pages/`
  - 导出的分享页面或原始 HTML

## 维护约定

- 原则、文档分层和产物规范统一写在 `PROJECT_RULES.md`，不要再分散复制。
- 影响当前决策的文档保留在根目录或活跃 `docs/` 目录。
- 历史材料默认归档，不默认删除。
- 环境、checkpoint、editable 第三方源码和其它重型产物不要放进仓库根目录。
