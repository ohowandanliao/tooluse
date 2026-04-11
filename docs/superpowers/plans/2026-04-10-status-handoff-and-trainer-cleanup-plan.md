# Status, Handoff, and Trainer Cleanup Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decide whether the legacy handwritten trainers should be removed now, and add top-level status and handoff markdown files so another Codex session can continue work safely on a different machine.

**Architecture:** First inspect the current trainer files and references so deletion is based on real dependency state instead of preference. Then write two top-level documents: one as the current project status board, and one as an operational handoff for another Codex or GPT session. If handwritten trainers are still not safe to delete, mark them as legacy and record the exact deletion gate in the docs.

**Tech Stack:** Markdown, Python repo structure, ripgrep, PyTest

---

### Task 1: Assess handwritten trainer deletion readiness

**Files:**
- Inspect: `src/schema_reuse/train/*.py`
- Inspect: `scripts/train_*.py`
- Inspect: `tests/train/test_train_configs.py`
- Inspect: `docs/**/*.md`

- [ ] **Step 1: Locate all current references to handwritten trainers**
- [ ] **Step 2: Check whether any non-legacy path still depends on them**
- [ ] **Step 3: Decide delete-now vs keep-as-legacy based on actual dependency state**

### Task 2: Add top-level status markdown

**Files:**
- Create: `STATUS.md`

- [ ] **Step 1: Summarize current scientific direction and implementation state**
- [ ] **Step 2: Record what is verified, what is blocked, and what is intentionally deferred**
- [ ] **Step 3: Record explicit deletion guidance for legacy handwritten trainers**

### Task 3: Add top-level handoff markdown

**Files:**
- Create: `HANDOFF.md`

- [ ] **Step 1: Document repo entry points and source-of-truth files**
- [ ] **Step 2: Document verified commands and expected outputs**
- [ ] **Step 3: Document immediate next steps for another Codex session on another machine**

### Task 4: Verify repository state after doc updates

**Files:**
- Verify: `STATUS.md`
- Verify: `HANDOFF.md`

- [ ] **Step 1: Re-run full test suite**
- [ ] **Step 2: Re-read the two top-level markdowns for consistency with current repo state**
