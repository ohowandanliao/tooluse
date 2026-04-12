from __future__ import annotations

import json
import re
from typing import Any

from schema_reuse.eval.metrics import accuracy, grouped_accuracy

_TOOL_CALL_PATTERN = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)
_CODE_BLOCK_PATTERN = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def _extract_payload(text: str) -> str:
    stripped = text.strip()
    tool_call_match = _TOOL_CALL_PATTERN.search(stripped)
    if tool_call_match:
        return tool_call_match.group(1).strip()

    code_block_match = _CODE_BLOCK_PATTERN.search(stripped)
    if code_block_match:
        return code_block_match.group(1).strip()

    return stripped


def _load_first_json_object(text: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            payload, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    raise ValueError("No JSON object found in text.")


def parse_tool_call(text: str) -> dict[str, Any]:
    payload = _load_first_json_object(_extract_payload(text))
    name = payload.get("name")
    arguments = payload.get("arguments")
    if not isinstance(name, str) or not name:
        raise ValueError("Tool call must contain a non-empty string `name`.")
    if not isinstance(arguments, dict):
        raise ValueError("Tool call must contain an object `arguments`.")
    return {
        "name": name,
        "arguments": {str(key): value for key, value in sorted(arguments.items())},
    }


def expand_processed_rows_for_mode(
    rows: list[dict[str, Any]],
    mode: str,
) -> list[dict[str, Any]]:
    if mode not in {"vanilla", "schema_augmented", "hammer_like"}:
        raise ValueError(f"Unsupported mode: {mode}")

    expanded: list[dict[str, Any]] = []
    for row in rows:
        variants = [("A", row["T_A"], row["y_A"])]
        if mode in {"schema_augmented", "hammer_like"}:
            variants.append(("B", row["T_B"], row["y_B"]))

        for schema_variant, schema, target_call in variants:
            expanded.append(
                {
                    "schema_variant": schema_variant,
                    "semantic_task_id": row.get("semantic_task_id"),
                    "transform_family": row.get("transform_family"),
                    "alias_split": row.get("alias_split"),
                    "source_benchmark": row.get("source_benchmark"),
                    "expected_tool_name": target_call.get("name"),
                    "expected_argument_keys": sorted(target_call.get("arguments", {}).keys()),
                    "schema_name": schema.get("name"),
                    "user": row.get("user"),
                }
            )
    return expanded


def evaluate_prediction_rows(
    rows: list[dict[str, Any]],
    *,
    metadata_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if metadata_rows is not None and len(metadata_rows) != len(rows):
        raise ValueError(
            "Prediction row count does not match metadata row count: "
            f"{len(rows)} != {len(metadata_rows)}"
        )

    exact_matches: list[bool] = []
    name_matches: list[bool] = []
    key_matches: list[bool] = []
    value_matches: list[bool] = []
    parsed_predictions: list[bool] = []
    records: list[dict[str, Any]] = []

    for index, row in enumerate(rows):
        label_call = parse_tool_call(row["label"])
        metadata = metadata_rows[index] if metadata_rows is not None else {}

        predicted_call: dict[str, Any] | None = None
        parse_error: str | None = None
        parsed = True
        try:
            predicted_call = parse_tool_call(row["predict"])
        except ValueError as exc:
            parsed = False
            parse_error = str(exc)

        exact_match = parsed and predicted_call == label_call
        name_match = parsed and predicted_call["name"] == label_call["name"]
        key_match = parsed and sorted(predicted_call["arguments"].keys()) == sorted(
            label_call["arguments"].keys()
        )
        value_match = parsed and predicted_call["arguments"] == label_call["arguments"]

        exact_matches.append(exact_match)
        name_matches.append(name_match)
        key_matches.append(key_match)
        value_matches.append(value_match)
        parsed_predictions.append(parsed)

        records.append(
            {
                "index": index,
                "prompt": row.get("prompt"),
                "prediction_parsed": parsed,
                "prediction_parse_error": parse_error,
                "predicted_call": predicted_call,
                "reference_call": label_call,
                "exact_match": exact_match,
                "name_match": name_match,
                "argument_key_exact_match": key_match,
                "argument_value_exact_match": value_match,
                **metadata,
            }
        )

    metrics: dict[str, Any] = {
        "count": len(rows),
        "parsed_prediction_rate": accuracy(parsed_predictions),
        "parsed_prediction_count": int(sum(parsed_predictions)),
        "exact_match_rate": accuracy(exact_matches),
        "exact_match_count": int(sum(exact_matches)),
        "name_match_rate": accuracy(name_matches),
        "argument_key_exact_match_rate": accuracy(key_matches),
        "argument_value_exact_match_rate": accuracy(value_matches),
    }

    if metadata_rows:
        schema_variants = [record["schema_variant"] for record in records]
        transform_families = [record["transform_family"] or "unknown" for record in records]
        metrics["exact_match_by_schema_variant"] = grouped_accuracy(
            exact_matches,
            schema_variants,
        )
        metrics["exact_match_by_transform_family"] = grouped_accuracy(
            exact_matches,
            transform_families,
        )

    return {"metrics": metrics, "records": records}
