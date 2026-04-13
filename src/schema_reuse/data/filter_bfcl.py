from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


ARGUMENT_REFERENCE_TEMPLATE = r"(?:`{token}`|\b{token}\b\s*[:=])"


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def _tool_names(sample: dict[str, Any]) -> set[str]:
    tools = set(sample.get("tools", []))
    ground_truth = sample.get("ground_truth", {})
    name = ground_truth.get("name")
    if isinstance(name, str) and name:
        tools.add(name)
    return {tool.lower() for tool in tools if isinstance(tool, str) and tool}


def _argument_names(sample: dict[str, Any]) -> set[str]:
    ground_truth = sample.get("ground_truth", {})
    arguments = ground_truth.get("arguments", {})
    return {
        key.lower()
        for key in arguments
        if isinstance(key, str) and key and len(key) > 2
    }


def mentions_schema_surface_forms(sample: dict[str, Any]) -> bool:
    user = normalize_text(sample.get("user", ""))
    for tool_name in _tool_names(sample):
        if re.search(rf"\b{re.escape(tool_name)}\b", user):
            return True
    for argument_name in _argument_names(sample):
        pattern = ARGUMENT_REFERENCE_TEMPLATE.format(token=re.escape(argument_name))
        if re.search(pattern, user):
            return True
    return False


def has_verifiable_ground_truth(sample: dict[str, Any]) -> bool:
    metadata = sample.get("metadata", {})
    return bool(metadata.get("executable") or metadata.get("ast_verifiable"))


def candidate_audit(sample: dict[str, Any]) -> dict[str, Any]:
    metadata = sample.get("metadata", {})
    if not metadata.get("single_turn", False):
        return {"is_valid": False, "reason": "not_single_turn"}
    if not has_verifiable_ground_truth(sample):
        return {"is_valid": False, "reason": "not_verifiable"}
    if mentions_schema_surface_forms(sample):
        return {"is_valid": False, "reason": "mentions_schema_surface_forms"}
    return {"is_valid": True, "reason": None}


def is_valid_candidate(sample: dict[str, Any]) -> bool:
    return bool(candidate_audit(sample)["is_valid"])


def build_semantic_task_id(sample: dict[str, Any]) -> str:
    ground_truth = sample.get("ground_truth", {})
    payload = {
        "user": normalize_text(sample.get("user", "")),
        "arguments": ground_truth.get("arguments", {}),
    }
    digest = hashlib.sha1(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return f"task_{digest[:12]}"


def build_candidate_record(
    sample: dict[str, Any],
    *,
    source_benchmark: str,
    split_group_id: str | None = None,
) -> dict[str, Any]:
    audit = candidate_audit(sample)
    record = dict(sample)
    record["semantic_task_id"] = build_semantic_task_id(sample)
    record["audit_status"] = "accepted" if audit["is_valid"] else "rejected"
    if audit["reason"] is not None:
        record["audit_reason"] = audit["reason"]
    if split_group_id is not None:
        record["split_group_id"] = split_group_id
    record["source_benchmark"] = source_benchmark
    return record
