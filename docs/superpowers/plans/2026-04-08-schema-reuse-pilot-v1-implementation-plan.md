# Schema-Reusable Decision Pilot V1 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the smallest reproducible pilot that can falsify or support the `cross-schema decision reuse` thesis on an audit-aware, single-turn function-calling slice.

**Architecture:** The pilot has three layers. First, build a clean paired-schema dataset with strict split hygiene and held-out alias transforms. Second, implement two evaluation tracks: a `reuse-identifiability` track for models that admit fixed-`d` `A->B`, and a separate `robustness-payoff` track for all methods on held-out target schemas. Third, train the minimum baseline families plus one main reuse model on the same backbone and judge the thesis only from the pre-registered gate report.

**Tech Stack:** Python 3.11, PyTorch, Hugging Face Transformers, PEFT/LoRA, JSONL, PyYAML, Pandas, PyTest

---

## Practical Resource Envelope

Assume the pilot stays on a single `7B-8B` instruct backbone with `LoRA/PEFT`.

Recommended server:

- `1x A100 80GB` or `1x H100 80GB`
- `24-32 vCPU`
- `128GB RAM`
- `1TB NVMe SSD`

Minimum workable server:

- `1x 48GB` GPU such as `RTX 6000 Ada`
- `16-24 vCPU`
- `64GB RAM`
- `500GB-1TB NVMe SSD`

Rough full-pilot budget:

- `50-100 GPU-hours` on an `80GB` card
- `80-160 GPU-hours` on a strong `48GB` card

Do not escalate to `14B+`, multi-GPU, or full fine-tuning before this pilot produces a clear go/no-go result.

## Scope Lock

This plan is only for `pilot-v1`.

Included:

- audit-aware single-turn executable function-calling data
- `G_main = {tool rename, argument rename, schema key reorder}`
- direct baselines
- latent baselines
- fixed-`d` reuse model
- counterfactual evaluation and pilot kill report

Excluded from this plan:

- BFCL-v3 multi-turn main table
- `description paraphrase`
- `argument reshaping`
- `EFPD`
- `RL`
- rerank / verifier / best-of-n

## Locked Decisions

These choices should be fixed before code starts moving:

- Use one backbone family for the whole pilot and record it in `configs/common/model.yaml`
- Use one decoding policy for all methods and all counterfactual variants
- Split by `semantic_task_id` before generating paired schemas
- Use held-out alias vocabularies and held-out transform seeds for the test split
- Treat `A->B` versus `shuffle/null` as the primary scientific gate only for methods that admit fixed-`d` `A->B`
- Do not place direct baselines in the same fixed-`d` `A->B` table unless a truly symmetric protocol exists
- Treat `rename+arg` as a mandatory pass slice, not a nice-to-have breakdown

## File Structure

Planned repo layout:

- Create: `pyproject.toml`
- Create: `configs/common/model.yaml`
- Create: `configs/pilot_v1/data.yaml`
- Create: `configs/pilot_v1/decode.yaml`
- Create: `configs/pilot_v1/train/direct.yaml`
- Create: `configs/pilot_v1/train/hammer_like.yaml`
- Create: `configs/pilot_v1/train/latent_bottleneck.yaml`
- Create: `configs/pilot_v1/train/latent_consistency.yaml`
- Create: `configs/pilot_v1/train/reuse.yaml`
- Create: `src/schema_reuse/__init__.py`
- Create: `src/schema_reuse/settings.py`
- Create: `src/schema_reuse/data/filter_bfcl.py`
- Create: `src/schema_reuse/data/alias_vocab.py`
- Create: `src/schema_reuse/data/transforms.py`
- Create: `src/schema_reuse/data/pairs.py`
- Create: `src/schema_reuse/models/bottleneck.py`
- Create: `src/schema_reuse/models/direct_fc.py`
- Create: `src/schema_reuse/models/hammer_like.py`
- Create: `src/schema_reuse/models/reuse_model.py`
- Create: `src/schema_reuse/train/direct.py`
- Create: `src/schema_reuse/train/latent.py`
- Create: `src/schema_reuse/train/reuse.py`
- Create: `src/schema_reuse/eval/counterfactual.py`
- Create: `src/schema_reuse/eval/metrics.py`
- Create: `src/schema_reuse/eval/report.py`
- Create: `scripts/build_pilot_slice.py`
- Create: `scripts/build_paired_dataset.py`
- Create: `scripts/train_direct.py`
- Create: `scripts/train_latent.py`
- Create: `scripts/train_reuse.py`
- Create: `scripts/eval_counterfactual.py`
- Create: `scripts/aggregate_pilot_results.py`
- Create: `tests/test_smoke_import.py`
- Create: `tests/data/test_filter_bfcl.py`
- Create: `tests/data/test_transforms.py`
- Create: `tests/data/test_pairs.py`
- Create: `tests/eval/test_counterfactual.py`
- Create: `tests/models/test_bottleneck.py`
- Create: `tests/train/test_train_configs.py`
- Create: `reports/pilot_v1/README.md`

Output artifacts to standardize:

- `data/interim/pilot_v1/candidates.jsonl`
- `data/processed/pilot_v1/train.jsonl`
- `data/processed/pilot_v1/dev.jsonl`
- `data/processed/pilot_v1/test.jsonl`
- `runs/pilot_v1/<method>/<seed>/metrics.json`
- `runs/pilot_v1/<method>/<seed>/predictions.jsonl`
- `reports/pilot_v1/reuse_identifiability_report.md`
- `reports/pilot_v1/robustness_payoff_report.md`
- `reports/pilot_v1/pilot_v1_gate_report.md`

## Evaluation Contract

There are two evaluation tracks.

### Track R: Reuse-identifiability

Only these methods are required to enter Track R:

- `reuse_main`
- `matched_latent_bottleneck`
- `latent_consistency_only`

Track R must produce:

- `A_to_A_exec_acc`
- `B_to_B_exec_acc`
- `A_to_B_exec_acc`
- `A_to_B_ast_acc`
- `shuffle_exec_acc`
- `null_exec_acc`
- `cf_gap`

### Track P: Robustness-payoff

All methods must enter Track P.

Track P must produce:

- `heldout_B_exec_acc`
- `heldout_B_ast_acc`
- `heldout_B_gap`
- breakdowns for `rename_only`, `rename_arg`, `rename_arg_reorder`

Hard interpretation rules:

- direct baselines do not get compared to `reuse_main` in Track R unless a symmetric fixed-`d` protocol is later defined
- `B->B` is a ceiling and interpretability check, not a headline result
- any positive main verdict requires success on `rename_arg`, not only on `rename_only`

Every method must also report:

- backbone model id
- trainable parameter count
- optimizer steps
- max decode tokens
- retry count
- seeds used

## Task 1: Repository Bootstrap

**Files:**
- Create: `pyproject.toml`
- Create: `src/schema_reuse/__init__.py`
- Create: `src/schema_reuse/settings.py`
- Test: `tests/test_smoke_import.py`

- [ ] **Step 1: Write the failing smoke test**

```python
from schema_reuse.settings import PACKAGE_NAME


def test_package_name():
    assert PACKAGE_NAME == "schema_reuse"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_smoke_import.py -q`
Expected: `ModuleNotFoundError` or import failure

- [ ] **Step 3: Write minimal package bootstrap**

```python
# src/schema_reuse/settings.py
PACKAGE_NAME = "schema_reuse"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_smoke_import.py -q`
Expected: `1 passed`

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/schema_reuse/__init__.py src/schema_reuse/settings.py tests/test_smoke_import.py
git commit -m "chore: bootstrap schema reuse pilot package"
```

## Task 2: Audit-Aware Candidate Slice Builder

**Files:**
- Create: `configs/pilot_v1/data.yaml`
- Create: `src/schema_reuse/data/filter_bfcl.py`
- Create: `scripts/build_pilot_slice.py`
- Test: `tests/data/test_filter_bfcl.py`

- [ ] **Step 1: Write failing tests for candidate filtering**

```python
from schema_reuse.data.filter_bfcl import is_valid_candidate


def test_rejects_explicit_tool_mentions():
    sample = {"user": "call weather_lookup for Shanghai", "tools": ["weather_lookup"]}
    assert is_valid_candidate(sample) is False


def test_accepts_single_turn_executable_call():
    sample = {
        "user": "What is the weather in Shanghai tomorrow?",
        "ground_truth": {"name": "opaque_a", "arguments": {"city": "Shanghai", "day": "tomorrow"}},
        "metadata": {"single_turn": True, "ast_verifiable": True},
    }
    assert is_valid_candidate(sample) is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/data/test_filter_bfcl.py -q`
Expected: import failure or missing function failure

- [ ] **Step 3: Implement strict filter rules**

Filtering rules to encode:

- keep only single-turn entries
- require executable or AST-verifiable ground truth
- reject user prompts that explicitly name tools or arguments
- emit a stable `semantic_task_id`
- attach `audit_status` and `source_benchmark`

- [ ] **Step 4: Build a first candidate manifest**

Run: `python scripts/build_pilot_slice.py --config configs/pilot_v1/data.yaml`
Expected: `data/interim/pilot_v1/candidates.jsonl` exists with one row per candidate

- [ ] **Step 5: Commit**

```bash
git add configs/pilot_v1/data.yaml src/schema_reuse/data/filter_bfcl.py scripts/build_pilot_slice.py tests/data/test_filter_bfcl.py
git commit -m "feat: add audit-aware pilot candidate builder"
```

## Task 3: Alias Vocabulary and Transform Engine

**Files:**
- Create: `src/schema_reuse/data/alias_vocab.py`
- Create: `src/schema_reuse/data/transforms.py`
- Test: `tests/data/test_transforms.py`

- [ ] **Step 1: Write failing transform tests**

```python
from schema_reuse.data.transforms import build_transform, apply_transform


def test_transform_is_bijective_for_names():
    schema = {"name": "weather_lookup", "parameters": ["city", "day"]}
    transform = build_transform(schema, seed=7)
    mapped = apply_transform(schema, transform)
    assert mapped["name"] != "weather_lookup"
    assert len(set(transform["arg_map"].values())) == len(transform["arg_map"])


def test_test_vocab_is_disjoint_from_train_vocab():
    transform = build_transform({"name": "x", "parameters": ["a"]}, seed=1, split="test")
    assert transform["tool_map"]["x"].startswith("test_")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/data/test_transforms.py -q`
Expected: import failure or missing function failure

- [ ] **Step 3: Implement `G_main` only**

Transform engine requirements:

- tool renaming with opaque aliases
- argument renaming with opaque aliases
- schema key reorder
- split-specific alias vocabularies
- transform metadata with seed and composition id

- [ ] **Step 4: Re-run tests**

Run: `pytest tests/data/test_transforms.py -q`
Expected: all tests pass

- [ ] **Step 5: Commit**

```bash
git add src/schema_reuse/data/alias_vocab.py src/schema_reuse/data/transforms.py tests/data/test_transforms.py
git commit -m "feat: add held-out alias transform engine"
```

## Task 4: Paired Dataset Builder With Split Hygiene

**Files:**
- Create: `src/schema_reuse/data/pairs.py`
- Create: `scripts/build_paired_dataset.py`
- Test: `tests/data/test_pairs.py`

- [ ] **Step 1: Write failing split-hygiene tests**

```python
from schema_reuse.data.pairs import split_candidates


def test_semantic_task_ids_do_not_cross_splits():
    rows = [
        {"semantic_task_id": "t1"},
        {"semantic_task_id": "t1"},
        {"semantic_task_id": "t2"},
    ]
    splits = split_candidates(rows, seed=11)
    train_ids = {row["semantic_task_id"] for row in splits["train"]}
    test_ids = {row["semantic_task_id"] for row in splits["test"]}
    assert train_ids.isdisjoint(test_ids)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/data/test_pairs.py -q`
Expected: import failure or missing function failure

- [ ] **Step 3: Implement paired-schema dataset build**

Dataset builder requirements:

- split by `semantic_task_id` before transform generation
- generate `T_A`, `T_B`, `y_A`, `y_B`
- attach `transform_seed`, `transform_family`, `alias_split`
- write `train.jsonl`, `dev.jsonl`, `test.jsonl`

- [ ] **Step 4: Build processed datasets**

Run: `python scripts/build_paired_dataset.py --config configs/pilot_v1/data.yaml`
Expected: processed train/dev/test JSONL files exist

- [ ] **Step 5: Commit**

```bash
git add src/schema_reuse/data/pairs.py scripts/build_paired_dataset.py tests/data/test_pairs.py
git commit -m "feat: add paired dataset builder with split hygiene"
```

## Task 5: Counterfactual Evaluator and Controls

**Files:**
- Create: `configs/pilot_v1/decode.yaml`
- Create: `src/schema_reuse/eval/counterfactual.py`
- Create: `src/schema_reuse/eval/metrics.py`
- Create: `scripts/eval_counterfactual.py`
- Test: `tests/eval/test_counterfactual.py`

- [ ] **Step 1: Write failing evaluator tests**

```python
from schema_reuse.eval.counterfactual import compute_counterfactual_metrics


def test_counterfactual_report_has_required_keys():
    report = compute_counterfactual_metrics(
        a_to_a=[1, 0],
        b_to_b=[1, 1],
        a_to_b=[1, 0],
        shuffle=[0, 0],
        null=[0, 0],
    )
    assert set(report) >= {
        "A_to_A_exec_acc",
        "B_to_B_exec_acc",
        "A_to_B_exec_acc",
        "shuffle_exec_acc",
        "null_exec_acc",
        "cf_gap",
    }
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/eval/test_counterfactual.py -q`
Expected: import failure or missing function failure

- [ ] **Step 3: Implement evaluator with fixed decode contract**

Evaluator requirements:

- support Track R and Track P as separate report modes
- compute `A->A`, `B->B`, `A->B`, `shuffle`, `null` for Track R only
- compute `CF-Gap = B->B - A->B` for Track R only
- compute held-out presented-schema metrics for all methods in Track P
- break down metrics by transform family
- persist per-example predictions and aggregate metrics

- [ ] **Step 4: Run tests and one toy evaluation**

Run: `pytest tests/eval/test_counterfactual.py -q`
Expected: tests pass

Run: `python scripts/eval_counterfactual.py --help`
Expected: CLI exposes run directory, dataset path, and decode config

- [ ] **Step 5: Commit**

```bash
git add configs/pilot_v1/decode.yaml src/schema_reuse/eval/counterfactual.py src/schema_reuse/eval/metrics.py scripts/eval_counterfactual.py tests/eval/test_counterfactual.py
git commit -m "feat: add counterfactual evaluator and controls"
```

## Task 6: Direct Baselines

**Files:**
- Create: `configs/pilot_v1/train/direct.yaml`
- Create: `src/schema_reuse/models/direct_fc.py`
- Create: `src/schema_reuse/train/direct.py`
- Create: `scripts/train_direct.py`
- Test: `tests/train/test_train_configs.py`

- [ ] **Step 1: Write failing config validation tests**

```python
from schema_reuse.train.direct import load_train_config


def test_direct_config_exposes_baseline_mode():
    config = load_train_config("configs/pilot_v1/train/direct.yaml")
    assert config["mode"] in {"vanilla_sft", "schema_augmented_sft"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/train/test_train_configs.py -q`
Expected: import failure or missing function failure

- [ ] **Step 3: Implement both direct baselines behind one trainer**

Required modes:

- `vanilla_sft`
- `schema_augmented_sft`

Invariants:

- same backbone
- same optimizer step budget
- same decode config

Evaluation rule:

- direct baselines are judged in Track P by held-out presented-schema robustness
- they are not automatically entitled to a Track R `A->B` number

- [ ] **Step 4: Smoke run both modes on a tiny sample**

Run: `python scripts/train_direct.py --config configs/pilot_v1/train/direct.yaml --mode vanilla_sft --max-steps 2`
Expected: run directory is created without crashing

Run: `python scripts/train_direct.py --config configs/pilot_v1/train/direct.yaml --mode schema_augmented_sft --max-steps 2`
Expected: run directory is created without crashing

- [ ] **Step 5: Commit**

```bash
git add configs/pilot_v1/train/direct.yaml src/schema_reuse/models/direct_fc.py src/schema_reuse/train/direct.py scripts/train_direct.py tests/train/test_train_configs.py
git commit -m "feat: add direct function-calling baselines"
```

## Task 7: Hammer-Like Baseline

**Files:**
- Create: `configs/pilot_v1/train/hammer_like.yaml`
- Create: `src/schema_reuse/models/hammer_like.py`
- Modify: `src/schema_reuse/train/direct.py`
- Test: `tests/train/test_train_configs.py`

- [ ] **Step 1: Extend tests for masking and irrelevant-tool perturbation**

```python
from schema_reuse.train.direct import load_train_config


def test_hammer_like_config_enables_name_masking():
    config = load_train_config("configs/pilot_v1/train/hammer_like.yaml")
    assert config["name_mask_probability"] > 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/train/test_train_configs.py -q`
Expected: missing config key or missing file failure

- [ ] **Step 3: Implement minimal Hammer-like recipe**

Recipe requirements:

- schema name masking during training
- irrelevant-tool injection during training or evaluation prep
- no extra backbone or decode advantage

- [ ] **Step 4: Smoke run the baseline**

Run: `python scripts/train_direct.py --config configs/pilot_v1/train/hammer_like.yaml --mode hammer_like --max-steps 2`
Expected: run directory is created without crashing

- [ ] **Step 5: Commit**

```bash
git add configs/pilot_v1/train/hammer_like.yaml src/schema_reuse/models/hammer_like.py src/schema_reuse/train/direct.py tests/train/test_train_configs.py
git commit -m "feat: add hammer-like schema robustness baseline"
```

## Task 8: Latent Baselines

**Files:**
- Create: `configs/pilot_v1/train/latent_bottleneck.yaml`
- Create: `configs/pilot_v1/train/latent_consistency.yaml`
- Create: `src/schema_reuse/models/bottleneck.py`
- Create: `src/schema_reuse/train/latent.py`
- Create: `scripts/train_latent.py`
- Test: `tests/models/test_bottleneck.py`

- [ ] **Step 1: Write failing bottleneck tests**

```python
from schema_reuse.models.bottleneck import BottleneckConfig


def test_bottleneck_config_is_capacity_bounded():
    config = BottleneckConfig(latent_dim=64)
    assert config.latent_dim <= 128
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/models/test_bottleneck.py -q`
Expected: import failure or missing class failure

- [ ] **Step 3: Implement two latent baselines**

Required modes:

- `matched_latent_bottleneck`
- `latent_consistency_only`

Invariants:

- same latent capacity as the main reuse model
- no `A->B` fixed-`d` objective in these baselines

- [ ] **Step 4: Smoke run both latent baselines**

Run: `python scripts/train_latent.py --config configs/pilot_v1/train/latent_bottleneck.yaml --max-steps 2`
Expected: run directory is created without crashing

Run: `python scripts/train_latent.py --config configs/pilot_v1/train/latent_consistency.yaml --max-steps 2`
Expected: run directory is created without crashing

- [ ] **Step 5: Commit**

```bash
git add configs/pilot_v1/train/latent_bottleneck.yaml configs/pilot_v1/train/latent_consistency.yaml src/schema_reuse/models/bottleneck.py src/schema_reuse/train/latent.py scripts/train_latent.py tests/models/test_bottleneck.py
git commit -m "feat: add latent baseline trainers"
```

## Task 9: Main Fixed-`d` Reuse Model

**Files:**
- Create: `configs/pilot_v1/train/reuse.yaml`
- Create: `src/schema_reuse/models/reuse_model.py`
- Create: `src/schema_reuse/train/reuse.py`
- Create: `scripts/train_reuse.py`
- Test: `tests/models/test_bottleneck.py`

- [ ] **Step 1: Extend tests for reuse-specific config**

```python
from schema_reuse.models.bottleneck import BottleneckConfig


def test_reuse_config_enables_cross_schema_objective():
    config = BottleneckConfig(latent_dim=64, enable_reuse=True)
    assert config.enable_reuse is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/models/test_bottleneck.py -q`
Expected: missing field or missing trainer failure

- [ ] **Step 3: Implement the smallest valid reuse trainer**

Training contract:

- encode under `T_A`
- decode under `T_A`
- decode under `T_B` without re-encoding
- optionally compute `B->B` oracle only for evaluation
- log latent dimension and trainable parameter count

- [ ] **Step 4: Smoke run the reuse trainer**

Run: `python scripts/train_reuse.py --config configs/pilot_v1/train/reuse.yaml --max-steps 2`
Expected: run directory is created without crashing

- [ ] **Step 5: Commit**

```bash
git add configs/pilot_v1/train/reuse.yaml src/schema_reuse/models/reuse_model.py src/schema_reuse/train/reuse.py scripts/train_reuse.py tests/models/test_bottleneck.py
git commit -m "feat: add fixed-d reuse training loop"
```

## Task 10: Aggregation, Gate Report, and Pre-Registered Verdict

**Files:**
- Create: `src/schema_reuse/eval/report.py`
- Create: `scripts/aggregate_pilot_results.py`
- Create: `reports/pilot_v1/README.md`

- [ ] **Step 1: Write a failing report aggregation test**

```python
from schema_reuse.eval.report import classify_gate_result


def test_gate_result_flags_failed_reuse():
    verdict = classify_gate_result(
        a_to_b=0.41,
        shuffle=0.39,
        null=0.37,
        hammer_like=0.45,
        latent_bottleneck=0.44,
    )
    assert verdict["status"] == "fail"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/eval/test_counterfactual.py tests/train/test_train_configs.py -q`
Expected: missing report function failure

- [ ] **Step 3: Implement the aggregation and gate logic**

Gate logic to encode:

- fail if Track R `A->B` is not clearly above `shuffle` and `null`
- fail if `B->B` is too weak to make `CF-Gap` interpretable
- fail if `CF-Gap` is not better than both `matched_latent_bottleneck` and `latent_consistency_only`
- fail if Track P on `rename_arg` does not beat both `schema_augmented_sft` and `hammer_like`
- warn if `A->A` regresses by more than the tolerated internal threshold

- [ ] **Step 4: Produce the first pilot report**

Run: `python scripts/aggregate_pilot_results.py --runs-dir runs/pilot_v1 --output reports/pilot_v1/pilot_v1_gate_report.md`
Expected: report contains a single verdict: `continue`, `rewrite`, or `stop`

- [ ] **Step 5: Commit**

```bash
git add src/schema_reuse/eval/report.py scripts/aggregate_pilot_results.py reports/pilot_v1/README.md
git commit -m "feat: add pilot gate report aggregation"
```

## Execution Order

Do not reorder these phases:

1. bootstrap
2. candidate slice
3. transform engine
4. paired dataset build
5. evaluator
6. direct baselines
7. Hammer-like baseline
8. latent baselines
9. reuse model
10. aggregation and gate report

Reason:

- Tasks 1-5 make the pilot falsifiable
- Tasks 6-8 define the minimum competitive floor
- Task 9 is only meaningful once the floor is real
- Task 10 decides whether the project should continue

## Required Run Matrix

Minimum pilot matrix:

- `vanilla_sft`
- `schema_augmented_sft`
- `hammer_like`
- `matched_latent_bottleneck`
- `latent_consistency_only`
- `reuse_main`

Required seeds:

- `0`
- `1`
- `2`

Required evaluations:

- Track R: `A->A`, `B->B`, `A->B`, `shuffle`, `null`, `CF-Gap`
- Track P: held-out presented-schema robustness
- breakdown by `rename_only`, `rename_arg`, `rename_arg_reorder`
- held-out alias vocabulary
- held-out transform seed
- irrelevant-tool injection probe

## Stop Conditions

Stop the entire line and rewrite the idea if any of these remain true after the minimum run matrix:

- `reuse_main` does not beat `shuffle` and `null` by a meaningful margin in Track R
- `B->B` is too weak to interpret `CF-Gap`
- `reuse_main` does not reduce `CF-Gap` relative to both `matched_latent_bottleneck` and `latent_consistency_only`
- `schema_augmented_sft` or `hammer_like` already explain the gain in Track P
- the effect does not survive `rename_arg`
- the benefit disappears on held-out aliases
- the method only works by enlarging `d` until it becomes an unconstrained code
- direct-vs-reuse comparison cannot be written into a clean two-track evaluation contract

## Handoff Notes

The plan assumes the thesis document at:

- `/Users/huangyixuan/Documents/tooluse/2026-03-31-nips2026-function-calling-idea-draft-v2.md`

should remain the canonical scientific statement, while this plan is the execution document.

Before any phase-2 idea is touched, `reports/pilot_v1/pilot_v1_gate_report.md` must exist and must say `continue`.
