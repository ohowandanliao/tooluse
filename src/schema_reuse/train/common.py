from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from schema_reuse.data.filter_bfcl import load_jsonl, write_jsonl
from schema_reuse.train.backend import probe_training_backend


def load_json_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _recursive_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _recursive_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def resolve_train_config(path: str | Path) -> dict[str, Any]:
    config = load_json_config(path)
    model_config_path = config.get("model_config_path")
    decode_config_path = config.get("decode_config_path")

    model_config = load_json_config(model_config_path) if model_config_path else {}
    decode_config = load_json_config(decode_config_path) if decode_config_path else {}

    merged = _recursive_merge(model_config, config)
    merged["model_config"] = model_config
    merged["decode_config"] = decode_config
    merged["config_path"] = str(path)
    return merged


def load_dataset_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    return load_jsonl(config["dataset_path"])


def ensure_run_dir(run_root: str | Path, method_name: str, seed: int) -> Path:
    run_dir = Path(run_root) / method_name / f"seed_{seed}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)


def write_predictions(path: str | Path, predictions: list[dict[str, Any]]) -> None:
    write_jsonl(path, predictions)


def build_common_metrics(
    config: dict[str, Any],
    *,
    method_name: str,
    max_steps: int,
    num_examples: int,
    extra_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    backend_report = probe_training_backend()
    metrics = {
        "status": "smoke_only_no_model",
        "method_name": method_name,
        "backbone_model_id": config.get("backbone_model_id"),
        "trainable_parameter_count": config.get("trainable_parameter_count"),
        "optimizer_steps": min(max_steps, num_examples),
        "optimizer_steps_budget": config.get("optimizer_steps_budget"),
        "max_decode_tokens": config.get("decode_config", {}).get("max_decode_tokens"),
        "retry_count": config.get("decode_config", {}).get("retry_count"),
        "seed": config.get("seed", 0),
        "num_examples": num_examples,
        "training_backend": backend_report.to_dict(),
    }
    if extra_metrics:
        metrics.update(extra_metrics)
    return metrics
