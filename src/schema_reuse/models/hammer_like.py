from __future__ import annotations

from copy import deepcopy
from typing import Any


def mask_schema_name(schema: dict[str, Any], *, placeholder: str = "<masked_tool>") -> dict[str, Any]:
    masked = deepcopy(schema)
    masked["name"] = placeholder
    return masked


def inject_irrelevant_tools(
    schema: dict[str, Any],
    *,
    count: int,
) -> list[dict[str, Any]]:
    tools = [deepcopy(schema)]
    for index in range(count):
        tools.append(
            {
                "name": f"irrelevant_tool_{index}",
                "parameters": [f"unused_arg_{index}"],
            }
        )
    return tools
