from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from schema_reuse.data.bfcl_official import resolve_env_path, select_target_tool_spec
from schema_reuse.data.filter_bfcl import load_jsonl


def _load_json_like(value: Any, *, field_name: str) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError(f"malformed_{field_name}") from exc
    return value


def _normalize_xlam_row_id(value: Any) -> str:
    if isinstance(value, bool):
        raise ValueError("missing_id")
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str) and value:
        return value
    raise ValueError("missing_id")


def load_xlam_rows(path: str | Path) -> list[dict[str, Any]]:
    resolved_path = resolve_env_path(path)
    if resolved_path.suffix in {".jsonl", ".ndjson"}:
        return load_jsonl(resolved_path)

    with resolved_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("train"), list):
        return payload["train"]
    raise ValueError(f"Unsupported xLAM payload structure: {resolved_path}")


def normalize_xlam_tool_spec(tool_spec: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(tool_spec, dict):
        raise ValueError("tool_spec_not_dict")

    tool_name = tool_spec.get("name")
    if not isinstance(tool_name, str) or not tool_name:
        raise ValueError("missing_tool_name")

    description = tool_spec.get("description", "")
    if not isinstance(description, str):
        description = ""

    raw_parameters = _load_json_like(tool_spec.get("parameters", {}), field_name="tool_parameters")
    if not isinstance(raw_parameters, dict):
        raise ValueError("tool_parameters_not_dict")

    properties: dict[str, Any] = {}
    required: list[str] = []
    for parameter_name, parameter_spec in raw_parameters.items():
        if not isinstance(parameter_name, str) or not parameter_name:
            raise ValueError("invalid_parameter_name")
        if not isinstance(parameter_spec, dict):
            raise ValueError("parameter_spec_not_dict")
        normalized_parameter = deepcopy(parameter_spec)
        if "required" in normalized_parameter:
            if normalized_parameter.pop("required"):
                required.append(parameter_name)
        if "type" not in normalized_parameter:
            normalized_parameter["type"] = "string"
        properties[parameter_name] = normalized_parameter

    return {
        "name": tool_name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }


def normalize_xlam_answer(answer: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(answer, dict):
        raise ValueError("answer_not_dict")

    tool_name = answer.get("name")
    if not isinstance(tool_name, str) or not tool_name:
        raise ValueError("missing_answer_name")

    arguments = _load_json_like(answer.get("arguments", {}), field_name="answer_arguments")
    if not isinstance(arguments, dict):
        raise ValueError("answer_arguments_not_dict")

    return {
        "name": tool_name,
        "arguments": deepcopy(arguments),
    }


def build_xlam_sample(
    row: dict[str, Any],
    *,
    source_benchmark: str,
    require_single_answer: bool = True,
) -> dict[str, Any]:
    row_id = _normalize_xlam_row_id(row.get("id"))

    query = row.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("missing_query")

    raw_tools = _load_json_like(row.get("tools"), field_name="tools")
    if not isinstance(raw_tools, list) or not raw_tools:
        raise ValueError("missing_tools")
    tool_pool_spec = [normalize_xlam_tool_spec(tool_spec) for tool_spec in raw_tools]

    raw_answers = _load_json_like(row.get("answers"), field_name="answers")
    if not isinstance(raw_answers, list) or not raw_answers:
        raise ValueError("missing_answers")
    if require_single_answer and len(raw_answers) != 1:
        raise ValueError("not_single_answer")
    normalized_answers = [normalize_xlam_answer(answer) for answer in raw_answers]

    ground_truth = normalized_answers[0]
    tool_spec = select_target_tool_spec(tool_pool_spec, target_tool_name=ground_truth["name"])

    return {
        "sample_id": row_id,
        "user": query.strip(),
        "ground_truth": ground_truth,
        "possible_ground_truth": deepcopy(normalized_answers),
        "tools": [tool["name"] for tool in tool_pool_spec],
        "tool_spec": tool_spec,
        "tool_pool_spec": tool_pool_spec,
        "metadata": {
            "single_turn": True,
            "ast_verifiable": True,
            "xlam_id": row_id,
            "num_tools": len(tool_pool_spec),
            "num_answers": len(normalized_answers),
        },
        "source_benchmark": source_benchmark,
    }
