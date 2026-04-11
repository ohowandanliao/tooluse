from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

from schema_reuse.data.filter_bfcl import load_jsonl, write_jsonl
from schema_reuse.data.transforms import DEFAULT_FAMILY, apply_transform, build_transform, transform_call


def _schema_from_call(call: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": call["name"],
        "parameters": list(call.get("arguments", {}).keys()),
    }


def split_candidates(
    rows: list[dict[str, Any]],
    *,
    seed: int,
    train_ratio: float = 0.8,
    dev_ratio: float = 0.1,
    test_ratio: float = 0.1,
) -> dict[str, list[dict[str, Any]]]:
    if not rows:
        return {"train": [], "dev": [], "test": []}

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["semantic_task_id"]].append(row)

    semantic_ids = list(grouped)
    rng = random.Random(seed)
    rng.shuffle(semantic_ids)

    n_ids = len(semantic_ids)
    train_cutoff = int(n_ids * train_ratio)
    dev_cutoff = train_cutoff + int(n_ids * dev_ratio)
    if n_ids > 1 and train_cutoff == n_ids:
        train_cutoff = n_ids - 1
    if dev_cutoff > n_ids:
        dev_cutoff = n_ids

    split_id_map = {
        "train": semantic_ids[:train_cutoff],
        "dev": semantic_ids[train_cutoff:dev_cutoff],
        "test": semantic_ids[dev_cutoff:],
    }

    if not split_id_map["train"]:
        split_id_map["train"] = semantic_ids[:1]
        split_id_map["test"] = semantic_ids[1:]

    return {
        split_name: [row for semantic_id in split_ids for row in grouped[semantic_id]]
        for split_name, split_ids in split_id_map.items()
    }


def build_pair_row(
    row: dict[str, Any],
    *,
    split: str,
    transform_seed: int,
    transform_family: str = DEFAULT_FAMILY,
) -> dict[str, Any]:
    y_a = row["ground_truth"]
    t_a = _schema_from_call(y_a)
    transform = build_transform(
        t_a,
        seed=transform_seed,
        split=split,
        family=transform_family,
    )
    t_b = apply_transform(t_a, transform)
    y_b = transform_call(y_a, transform)

    return {
        "semantic_task_id": row["semantic_task_id"],
        "user": row["user"],
        "T_A": t_a,
        "T_B": t_b,
        "y_A": y_a,
        "y_B": y_b,
        "transform_seed": transform_seed,
        "transform_family": transform_family,
        "alias_split": split,
        "source_benchmark": row.get("source_benchmark", "unknown"),
        "audit_status": row.get("audit_status", "accepted"),
        "metadata": row.get("metadata", {}),
    }


def build_processed_datasets(config: dict[str, Any]) -> dict[str, Path]:
    candidate_rows = load_jsonl(config["candidate_output_path"])
    split_rows = split_candidates(
        candidate_rows,
        seed=config["split_seed"],
        train_ratio=config.get("train_ratio", 0.8),
        dev_ratio=config.get("dev_ratio", 0.1),
        test_ratio=config.get("test_ratio", 0.1),
    )

    output_dir = Path(config["processed_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    written_paths: dict[str, Path] = {}
    for split_name, rows in split_rows.items():
        paired_rows = [
            build_pair_row(
                row,
                split=split_name,
                transform_seed=config["split_seed"] + index,
            )
            for index, row in enumerate(rows)
        ]
        output_path = output_dir / f"{split_name}.jsonl"
        write_jsonl(output_path, paired_rows)
        written_paths[split_name] = output_path

    return written_paths


def load_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)
