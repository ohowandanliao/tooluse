import json
import importlib.util
import sys
from pathlib import Path

from schema_reuse.data.xlam_official import build_xlam_sample


SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "build_xlam_fc_single_call_slice.py"
)
if str(SCRIPT_PATH.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT_PATH.parent))
SPEC = importlib.util.spec_from_file_location("build_xlam_fc_single_call_slice", SCRIPT_PATH)
assert SPEC is not None
assert SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
build_candidate_manifest = MODULE.build_candidate_manifest


def test_build_xlam_sample_parses_stringified_fields_and_normalizes_schema() -> None:
    row = {
        "id": "xlam_1",
        "query": "Book a table for four at Noma tonight.",
        "tools": json.dumps(
            [
                {
                    "name": "reserve_restaurant",
                    "description": "Reserve a table at a restaurant.",
                    "parameters": {
                        "restaurant_name": {
                            "type": "string",
                            "description": "Name of the restaurant.",
                            "required": True,
                        },
                        "party_size": {
                            "type": "int",
                            "description": "Number of guests.",
                            "required": True,
                        },
                        "time": {
                            "type": "string",
                            "description": "Requested reservation time.",
                            "required": False,
                        },
                    },
                }
            ]
        ),
        "answers": json.dumps(
            [
                {
                    "name": "reserve_restaurant",
                    "arguments": json.dumps(
                        {"restaurant_name": "Noma", "party_size": 4, "time": "19:00"}
                    ),
                }
            ]
        ),
    }

    sample = build_xlam_sample(
        row,
        source_benchmark="xlam_function_calling_60k_single_call",
    )

    assert sample["user"] == "Book a table for four at Noma tonight."
    assert sample["ground_truth"] == {
        "name": "reserve_restaurant",
        "arguments": {
            "restaurant_name": "Noma",
            "party_size": 4,
            "time": "19:00",
        },
    }
    assert sample["tool_spec"]["parameters"]["type"] == "object"
    assert sample["tool_spec"]["parameters"]["required"] == [
        "restaurant_name",
        "party_size",
    ]
    assert sample["metadata"]["single_turn"] is True
    assert sample["metadata"]["num_tools"] == 1
    assert sample["metadata"]["num_answers"] == 1


def test_build_xlam_sample_supports_native_json_objects_and_multi_tool_pool() -> None:
    row = {
        "id": "xlam_2",
        "query": "Check whether my flight AA100 lands on time.",
        "tools": [
            {
                "name": "lookup_weather",
                "description": "Fetch weather information.",
                "parameters": {
                    "city": {
                        "type": "string",
                        "description": "Target city.",
                        "required": True,
                    }
                },
            },
            {
                "name": "lookup_flight_status",
                "description": "Fetch flight status.",
                "parameters": {
                    "flight_number": {
                        "type": "string",
                        "description": "Flight number.",
                        "required": True,
                    }
                },
            },
        ],
        "answers": [
            {
                "name": "lookup_flight_status",
                "arguments": {"flight_number": "AA100"},
            }
        ],
    }

    sample = build_xlam_sample(
        row,
        source_benchmark="xlam_function_calling_60k_single_call",
    )

    assert sample["tool_spec"]["name"] == "lookup_flight_status"
    assert len(sample["tool_pool_spec"]) == 2
    assert sample["metadata"]["num_tools"] == 2


def test_build_xlam_sample_coerces_numeric_id_to_string() -> None:
    row = {
        "id": 42,
        "query": "Check whether my flight AA100 lands on time.",
        "tools": [
            {
                "name": "lookup_flight_status",
                "description": "Fetch flight status.",
                "parameters": {
                    "flight_number": {
                        "type": "string",
                        "description": "Flight number.",
                        "required": True,
                    }
                },
            }
        ],
        "answers": [
            {
                "name": "lookup_flight_status",
                "arguments": {"flight_number": "AA100"},
            }
        ],
    }

    sample = build_xlam_sample(
        row,
        source_benchmark="xlam_function_calling_60k_single_call",
    )

    assert sample["sample_id"] == "42"
    assert sample["metadata"]["xlam_id"] == "42"


def test_build_candidate_manifest_filters_to_single_call_audited_slice(
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "xlam.json"
    config_path = tmp_path / "config.json"
    rows = [
        {
            "id": "accepted",
            "query": "Book a table for four at Noma tonight.",
            "tools": [
                {
                    "name": "reserve_restaurant",
                    "description": "Reserve a table at a restaurant.",
                    "parameters": {
                        "restaurant_name": {
                            "type": "string",
                            "description": "Name of the restaurant.",
                            "required": True,
                        },
                        "party_size": {
                            "type": "int",
                            "description": "Number of guests.",
                            "required": True,
                        },
                    },
                }
            ],
            "answers": [
                {
                    "name": "reserve_restaurant",
                    "arguments": {"restaurant_name": "Noma", "party_size": 4},
                }
            ],
        },
        {
            "id": "multi_call",
            "query": "Compute both a sum and a product.",
            "tools": [
                {
                    "name": "sum_numbers",
                    "description": "Add numbers.",
                    "parameters": {
                        "values": {
                            "type": "list",
                            "description": "Values to sum.",
                            "required": True,
                        }
                    },
                },
                {
                    "name": "product_numbers",
                    "description": "Multiply numbers.",
                    "parameters": {
                        "values": {
                            "type": "list",
                            "description": "Values to multiply.",
                            "required": True,
                        }
                    },
                },
            ],
            "answers": [
                {"name": "sum_numbers", "arguments": {"values": [1, 2, 3]}},
                {"name": "product_numbers", "arguments": {"values": [2, 3, 5]}},
            ],
        },
        {
            "id": "surface_form",
            "query": "Use reserve_restaurant to book Noma for four people.",
            "tools": [
                {
                    "name": "reserve_restaurant",
                    "description": "Reserve a table at a restaurant.",
                    "parameters": {
                        "restaurant_name": {
                            "type": "string",
                            "description": "Name of the restaurant.",
                            "required": True,
                        },
                        "party_size": {
                            "type": "int",
                            "description": "Number of guests.",
                            "required": True,
                        },
                    },
                }
            ],
            "answers": [
                {
                    "name": "reserve_restaurant",
                    "arguments": {"restaurant_name": "Noma", "party_size": 4},
                }
            ],
        },
    ]
    input_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    config = {
        "input_path": str(input_path),
        "source_benchmark": "xlam_function_calling_60k_single_call",
        "candidate_output_path": str(tmp_path / "candidates.jsonl"),
        "audit_report_path": str(tmp_path / "audit.json"),
        "processed_dir": str(tmp_path / "processed"),
        "split_seed": 11,
        "split_group_strategy": "semantic_task",
        "require_single_answer": True,
    }
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = build_candidate_manifest(config_path)

    assert report["summary"]["accepted_candidate_count"] == 1
    assert report["summary"]["rejection_reasons"]["not_single_answer"] == 1
    assert report["summary"]["rejection_reasons"]["mentions_schema_surface_forms"] == 1
