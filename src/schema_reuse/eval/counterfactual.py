from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from schema_reuse.eval.metrics import accuracy, grouped_accuracy


def compute_counterfactual_metrics(
    *,
    a_to_a: list[int | float | bool],
    b_to_b: list[int | float | bool],
    a_to_b: list[int | float | bool],
    shuffle: list[int | float | bool],
    null: list[int | float | bool],
) -> dict[str, float]:
    a_to_a_acc = accuracy(a_to_a)
    b_to_b_acc = accuracy(b_to_b)
    a_to_b_acc = accuracy(a_to_b)

    return {
        "A_to_A_exec_acc": a_to_a_acc,
        "B_to_B_exec_acc": b_to_b_acc,
        "A_to_B_exec_acc": a_to_b_acc,
        "shuffle_exec_acc": accuracy(shuffle),
        "null_exec_acc": accuracy(null),
        "cf_gap": b_to_b_acc - a_to_b_acc,
    }


def compute_track_p_metrics(
    *,
    heldout_exec: list[int | float | bool],
    heldout_ast: list[int | float | bool],
    transform_families: list[str],
) -> dict[str, Any]:
    return {
        "heldout_B_exec_acc": accuracy(heldout_exec),
        "heldout_B_ast_acc": accuracy(heldout_ast),
        "heldout_B_gap": accuracy(heldout_ast) - accuracy(heldout_exec),
        "breakdown_exec": grouped_accuracy(heldout_exec, transform_families),
        "breakdown_ast": grouped_accuracy(heldout_ast, transform_families),
    }


def write_report(
    output_path: str | Path,
    *,
    metrics: dict[str, Any],
    predictions: list[dict[str, Any]] | None = None,
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"metrics": metrics, "predictions": predictions or []}
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
