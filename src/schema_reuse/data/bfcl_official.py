from __future__ import annotations

import hashlib
import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any

from schema_reuse.data.filter_bfcl import build_semantic_task_id, load_jsonl


_OMIT_ARGUMENT = object()


def resolve_env_path(path: str | Path) -> Path:
    expanded = os.path.expandvars(str(path))
    if "$" in expanded:
        raise ValueError(f"Unresolved environment variable in path: {path}")
    return Path(expanded)


def load_jsonl_by_id(path: str | Path) -> dict[str, dict[str, Any]]:
    rows = load_jsonl(path)
    keyed_rows: dict[str, dict[str, Any]] = {}
    for row in rows:
        row_id = row.get("id")
        if not isinstance(row_id, str) or not row_id:
            raise ValueError(f"Missing string id in {path}")
        if row_id in keyed_rows:
            raise ValueError(f"Duplicate id {row_id} in {path}")
        keyed_rows[row_id] = row
    return keyed_rows


def extract_single_turn_user(question: Any) -> str:
    if not isinstance(question, list) or len(question) != 1:
        raise ValueError("question_not_single_turn")
    turn = question[0]
    if not isinstance(turn, list):
        raise ValueError("question_turn_not_list")

    user_messages = []
    non_user_roles = 0
    for message in turn:
        if not isinstance(message, dict):
            raise ValueError("question_message_not_dict")
        role = message.get("role")
        content = message.get("content")
        if role == "user" and isinstance(content, str) and content.strip():
            user_messages.append(content.strip())
        elif role is not None:
            non_user_roles += 1

    if len(user_messages) != 1 or non_user_roles:
        raise ValueError("question_not_single_user_turn")
    return user_messages[0]


def _is_blank_option(value: Any) -> bool:
    return value == "" or value is None


def _canonicalize_selected_value(value: Any) -> Any:
    if isinstance(value, dict):
        canonicalized: dict[str, Any] = {}
        for key, nested_value in value.items():
            normalized_value = canonicalize_argument_value(nested_value)
            if normalized_value is _OMIT_ARGUMENT:
                continue
            canonicalized[str(key)] = normalized_value
        return canonicalized
    if isinstance(value, list):
        return [_canonicalize_selected_value(item) for item in value]
    return value


def canonicalize_argument_value(value: Any) -> Any:
    if not isinstance(value, list):
        return _canonicalize_selected_value(value)

    if any(_is_blank_option(option) for option in value):
        return _OMIT_ARGUMENT

    if not value:
        return []

    return _canonicalize_selected_value(value[0])


def canonicalize_ground_truth(
    ground_truth: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if not isinstance(ground_truth, list) or len(ground_truth) != 1:
        raise ValueError("not_single_call_ground_truth")

    entry = ground_truth[0]
    if not isinstance(entry, dict) or len(entry) != 1:
        raise ValueError("malformed_ground_truth_entry")

    tool_name, raw_arguments = next(iter(entry.items()))
    if not isinstance(tool_name, str) or not tool_name:
        raise ValueError("missing_tool_name")
    if not isinstance(raw_arguments, dict):
        raise ValueError("ground_truth_arguments_not_dict")

    canonical_arguments: dict[str, Any] = {}
    omitted_optional_arguments: list[str] = []
    for argument_name, value in raw_arguments.items():
        canonical_value = canonicalize_argument_value(value)
        if canonical_value is _OMIT_ARGUMENT:
            omitted_optional_arguments.append(str(argument_name))
            continue
        canonical_arguments[str(argument_name)] = canonical_value

    metadata = {"omitted_optional_arguments": sorted(omitted_optional_arguments)}
    return {"name": tool_name, "arguments": canonical_arguments}, metadata


def select_target_tool_spec(
    function_pool: list[dict[str, Any]],
    *,
    target_tool_name: str,
) -> dict[str, Any]:
    for tool_spec in function_pool:
        if tool_spec.get("name") == target_tool_name:
            return deepcopy(tool_spec)
    raise ValueError(f"target_tool_not_found:{target_tool_name}")


def _tool_argument_names(tool_spec: dict[str, Any]) -> list[str]:
    parameters = tool_spec.get("parameters", {})
    if isinstance(parameters, dict):
        properties = parameters.get("properties", {})
        if isinstance(properties, dict):
            return sorted(str(name) for name in properties.keys())
    return []


def build_split_group_id(
    sample: dict[str, Any],
    *,
    strategy: str,
) -> str:
    if strategy == "semantic_task":
        return sample.get("semantic_task_id", build_semantic_task_id(sample))

    if strategy == "tool_signature":
        payload = {
            "category": sample.get("metadata", {}).get("bfcl_category"),
            "tool_name": sample["ground_truth"]["name"],
            "argument_names": sorted(sample["ground_truth"].get("arguments", {}).keys()),
        }
    elif strategy == "tool_pool_signature":
        payload = {
            "category": sample.get("metadata", {}).get("bfcl_category"),
            "tool_pool": [
                {
                    "name": tool_spec.get("name"),
                    "argument_names": _tool_argument_names(tool_spec),
                }
                for tool_spec in sample.get("tool_pool_spec", [])
            ],
        }
    else:
        raise ValueError(f"Unsupported split group strategy: {strategy}")

    digest = hashlib.sha1(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return f"group_{digest[:12]}"


def build_bfcl_sample(
    question_row: dict[str, Any],
    answer_row: dict[str, Any],
    *,
    category_name: str,
    source_benchmark: str,
    language: str | None = None,
    require_single_tool: bool = True,
) -> dict[str, Any]:
    question_id = question_row.get("id")
    answer_id = answer_row.get("id")
    if question_id != answer_id:
        raise ValueError("mismatched_question_answer_ids")

    function_pool = question_row.get("function")
    if not isinstance(function_pool, list) or not function_pool:
        raise ValueError("missing_function_pool")
    if require_single_tool and len(function_pool) != 1:
        raise ValueError("not_single_tool")

    ground_truth, canonicalization = canonicalize_ground_truth(answer_row.get("ground_truth"))
    target_tool_spec = select_target_tool_spec(
        function_pool,
        target_tool_name=ground_truth["name"],
    )

    metadata = {
        "single_turn": True,
        "ast_verifiable": True,
        "bfcl_category": category_name,
        "bfcl_id": question_id,
        "num_tools": len(function_pool),
        "canonicalization": canonicalization,
    }
    if language is not None:
        metadata["language"] = language

    return {
        "sample_id": question_id,
        "user": extract_single_turn_user(question_row.get("question")),
        "ground_truth": ground_truth,
        "possible_ground_truth": deepcopy(answer_row.get("ground_truth")),
        "tools": [str(tool_spec.get("name")) for tool_spec in function_pool],
        "tool_spec": target_tool_spec,
        "tool_pool_spec": deepcopy(function_pool),
        "metadata": metadata,
        "source_benchmark": source_benchmark,
    }
