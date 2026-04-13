from __future__ import annotations

import random
from copy import deepcopy
from typing import Any

from schema_reuse.data.alias_vocab import build_alias_map


DEFAULT_FAMILY = "rename_arg_reorder"


def _schema_parameters(schema: dict[str, Any]) -> list[str]:
    parameters = schema.get("parameters")
    if isinstance(parameters, list):
        return [str(parameter) for parameter in parameters]
    if isinstance(parameters, dict):
        properties = parameters.get("properties")
        if isinstance(properties, dict):
            return [str(parameter) for parameter in properties.keys()]
    arguments = schema.get("arguments")
    if isinstance(arguments, dict):
        return [str(parameter) for parameter in arguments.keys()]
    return []


def build_transform(
    schema: dict[str, Any],
    *,
    seed: int,
    split: str = "train",
    family: str = DEFAULT_FAMILY,
) -> dict[str, Any]:
    tool_name = str(schema["name"])
    parameters = _schema_parameters(schema)
    rng = random.Random(f"{split}:{family}:{seed}:{tool_name}")
    key_order = ["name", "parameters"]
    if rng.random() >= 0.5:
        key_order.reverse()

    return {
        "tool_map": build_alias_map([tool_name], seed=seed, split=split, namespace="tool"),
        "arg_map": build_alias_map(parameters, seed=seed, split=split, namespace="arg"),
        "schema_key_order": key_order,
        "seed": seed,
        "split": split,
        "family": family,
        "composition_id": f"{split}:{family}:{seed}",
    }


def apply_transform(schema: dict[str, Any], transform: dict[str, Any]) -> dict[str, Any]:
    transformed = deepcopy(schema)
    transformed["name"] = transform["tool_map"].get(schema["name"], schema["name"])

    parameters = schema.get("parameters")
    if isinstance(parameters, list):
        transformed["parameters"] = [
            transform["arg_map"].get(parameter, parameter) for parameter in parameters
        ]
    elif isinstance(parameters, dict):
        transformed_parameters = deepcopy(parameters)
        properties = parameters.get("properties", {})
        if isinstance(properties, dict):
            transformed_parameters["properties"] = {
                transform["arg_map"].get(parameter_name, parameter_name): deepcopy(property_spec)
                for parameter_name, property_spec in properties.items()
            }
        required = parameters.get("required")
        if isinstance(required, list):
            transformed_parameters["required"] = [
                transform["arg_map"].get(parameter_name, parameter_name)
                for parameter_name in required
            ]
        transformed["parameters"] = transformed_parameters
    else:
        parameters = _schema_parameters(schema)
        transformed["parameters"] = [
            transform["arg_map"].get(parameter, parameter) for parameter in parameters
        ]
    ordered: dict[str, Any] = {}
    for key in transform.get("schema_key_order", ["name", "parameters"]):
        ordered[key] = transformed[key]

    for key, value in transformed.items():
        if key in ordered or key in {"name", "parameters", "arguments"}:
            continue
        ordered[key] = value

    return ordered


def transform_call(call: dict[str, Any], transform: dict[str, Any]) -> dict[str, Any]:
    arguments = {
        transform["arg_map"].get(argument_name, argument_name): argument_value
        for argument_name, argument_value in call.get("arguments", {}).items()
    }
    return {
        "name": transform["tool_map"].get(call["name"], call["name"]),
        "arguments": arguments,
    }
