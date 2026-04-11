# LLaMA-Factory Baseline Export Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Export the current pilot-v1 baseline data into LLaMA-Factory-compatible datasets and CLI configs without modifying LLaMA-Factory source code.

**Architecture:** Keep the project-specific logic inside this repo and treat LLaMA-Factory as the training runtime. The export layer converts processed paired-schema rows into ShareGPT/OpenAI-style datasets plus `dataset_info.json`, while CLI yaml files point LLaMA-Factory at those exported datasets. `reuse_main` stays out of this first integration pass.

**Tech Stack:** Python 3.10+, JSON/JSONL, PyTest, LLaMA-Factory CLI dataset conventions

---

### Task 1: Add Export Tests

**Files:**
- Create: `tests/export/test_llamafactory.py`
- Create: `src/schema_reuse/export/llamafactory.py`

- [ ] **Step 1: Write failing export tests**
- [ ] **Step 2: Run tests to verify they fail**
- [ ] **Step 3: Implement minimal exporter helpers**
- [ ] **Step 4: Run tests to verify they pass**

### Task 2: Add Baseline Export Script

**Files:**
- Create: `scripts/export_llamafactory_baselines.py`
- Modify: `src/schema_reuse/export/llamafactory.py`

- [ ] **Step 1: Add a failing smoke-style export test if needed**
- [ ] **Step 2: Implement baseline export script**
- [ ] **Step 3: Run exporter and verify output files exist**

### Task 3: Add CLI Config Templates

**Files:**
- Create: `configs/llamafactory/dataset_info.json`
- Create: `configs/llamafactory/qwen_baseline_lora_sft.yaml`
- Create: `docs/llamafactory-baseline.md`

- [ ] **Step 1: Write minimal dataset registration and CLI config templates**
- [ ] **Step 2: Document how to run baseline training with `llamafactory-cli`**
- [ ] **Step 3: Re-run full local verification**
