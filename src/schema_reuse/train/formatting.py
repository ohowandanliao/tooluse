from __future__ import annotations

import json
from typing import Any


def serialize_call(call: dict[str, Any]) -> str:
    return json.dumps(call, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def serialize_schema(schema: dict[str, Any]) -> str:
    return json.dumps(schema, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build_direct_example(
    row: dict[str, Any],
    *,
    schema_key: str,
    target_key: str,
) -> dict[str, str]:
    prompt = (
        "User Request:\n"
        f"{row['user']}\n\n"
        "Schema:\n"
        f"{serialize_schema(row[schema_key])}\n\n"
        "Return exactly one tool call as JSON.\n"
    )
    return {
        "prompt": prompt,
        "target": serialize_call(row[target_key]),
    }


def build_reuse_example(row: dict[str, Any]) -> dict[str, str]:
    prompt = (
        "User Request:\n"
        f"{row['user']}\n\n"
        "Source Schema:\n"
        f"{serialize_schema(row['T_A'])}\n\n"
        "Target Schema:\n"
        f"{serialize_schema(row['T_B'])}\n\n"
        "Return exactly one tool call under the target schema as JSON.\n"
    )
    return {
        "prompt": prompt,
        "target": serialize_call(row["y_B"]),
    }
