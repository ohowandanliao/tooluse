from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from schema_reuse.models.hammer_like import inject_irrelevant_tools
from schema_reuse.data.filter_bfcl import load_jsonl
from schema_reuse.train.formatting import serialize_call


TYPE_ALIASES = {
    "array": "array",
    "arraylist": "array",
    "bool": "boolean",
    "boolean": "boolean",
    "dict": "object",
    "double": "number",
    "float": "number",
    "hashmap": "object",
    "int": "integer",
    "integer": "integer",
    "long": "integer",
    "number": "number",
    "object": "object",
    "str": "string",
    "string": "string",
    "tuple": "array",
    "any": "string",
}


def _normalize_jsonschema_types(payload: Any) -> Any:
    if isinstance(payload, dict):
        normalized = {}
        for key, value in payload.items():
            if key == "type" and isinstance(value, str):
                normalized[key] = TYPE_ALIASES.get(value.lower(), value.lower())
            else:
                normalized[key] = _normalize_jsonschema_types(value)
        return normalized
    if isinstance(payload, list):
        return [_normalize_jsonschema_types(item) for item in payload]
    return payload


def schema_to_tool(schema: dict[str, Any]) -> dict[str, Any]:
    parameters = schema.get("parameters", [])
    if isinstance(parameters, dict) and isinstance(parameters.get("properties"), dict):
        return _normalize_jsonschema_types(deepcopy(schema))
    properties = {
        parameter: {
            "type": "string",
            "description": f"Argument `{parameter}`.",
        }
        for parameter in parameters
    }
    return {
        "name": schema["name"],
        "description": f"Tool schema for {schema['name']}.",
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": list(parameters),
        },
    }


def make_sharegpt_record(
    *,
    user: str,
    schema: dict[str, Any],
    target_call: dict[str, Any],
    tool_pool: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    tools = tool_pool or [schema]
    return {
        "conversations": [
            {"from": "human", "value": user},
            {"from": "function_call", "value": serialize_call(target_call)},
        ],
        "tools": json.dumps(
            [schema_to_tool(tool) for tool in tools],
            ensure_ascii=False,
            sort_keys=True,
        ),
    }


def _base_variants(row: dict[str, Any], mode: str) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    variants = [(deepcopy(row["T_A"]), deepcopy(row["y_A"]))]
    if mode in {"schema_augmented", "hammer_like"}:
        variants.append((deepcopy(row["T_B"]), deepcopy(row["y_B"])))
    return variants


def export_baseline_splits(
    splits: dict[str, list[dict[str, Any]]],
    *,
    irrelevant_tool_count: int = 2,
) -> dict[str, dict[str, list[dict[str, Any]]]]:
    exported: dict[str, dict[str, list[dict[str, Any]]]] = {}

    for split_name, rows in splits.items():
        exported[split_name] = {
            "vanilla": [],
            "schema_augmented": [],
            "hammer_like": [],
        }
        for row in rows:
            for schema, target_call in _base_variants(row, "vanilla"):
                exported[split_name]["vanilla"].append(
                    make_sharegpt_record(user=row["user"], schema=schema, target_call=target_call)
                )
            for schema, target_call in _base_variants(row, "schema_augmented"):
                exported[split_name]["schema_augmented"].append(
                    make_sharegpt_record(user=row["user"], schema=schema, target_call=target_call)
                )
            for schema, target_call in _base_variants(row, "hammer_like"):
                tool_pool = inject_irrelevant_tools(schema, count=irrelevant_tool_count)
                exported[split_name]["hammer_like"].append(
                    make_sharegpt_record(
                        user=row["user"],
                        schema=schema,
                        target_call=target_call,
                        tool_pool=tool_pool,
                    )
                )

    return exported


def build_dataset_info(train_files: dict[str, str]) -> dict[str, dict[str, Any]]:
    return {
        dataset_name: {
            "file_name": file_name,
            "formatting": "sharegpt",
            "columns": {
                "messages": "conversations",
                "tools": "tools",
            },
        }
        for dataset_name, file_name in train_files.items()
    }


def _write_json(path: str | Path, payload: Any) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)


def load_processed_splits(processed_dir: str | Path) -> dict[str, list[dict[str, Any]]]:
    processed_path = Path(processed_dir)
    return {
        split: load_jsonl(processed_path / f"{split}.jsonl")
        for split in ("train", "dev", "test")
    }


def export_baselines_to_directory(
    processed_dir: str | Path,
    output_dir: str | Path,
    *,
    irrelevant_tool_count: int = 2,
    dataset_prefix: str = "pilot_v1",
) -> dict[str, Any]:
    splits = load_processed_splits(processed_dir)
    exported = export_baseline_splits(splits, irrelevant_tool_count=irrelevant_tool_count)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    dataset_files: dict[str, str] = {}
    dataset_record_counts: dict[str, int] = {}
    split_alias = {"dev": "eval"}
    for split_name, modes in exported.items():
        split_label = split_alias.get(split_name, split_name)
        for mode_name, records in modes.items():
            dataset_name = f"{dataset_prefix}_{mode_name}_{split_label}"
            file_name = f"{dataset_name}.json"
            _write_json(output_path / file_name, records)
            dataset_files[dataset_name] = file_name
            dataset_record_counts[dataset_name] = len(records)

    dataset_info = build_dataset_info(dataset_files)
    _write_json(output_path / "dataset_info.json", dataset_info)
    empty_datasets = sorted(
        dataset_name
        for dataset_name, record_count in dataset_record_counts.items()
        if record_count == 0
    )
    return {
        "output_dir": str(output_path),
        "dataset_files": dataset_files,
        "dataset_record_counts": dataset_record_counts,
        "empty_datasets": empty_datasets,
        "dataset_info_path": str(output_path / "dataset_info.json"),
    }
