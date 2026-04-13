import json
from pathlib import Path

from schema_reuse.export.llamafactory import (
    build_dataset_info,
    export_baseline_splits,
    export_baselines_to_directory,
    make_sharegpt_record,
    schema_to_tool,
)


def test_make_sharegpt_record_contains_function_call_and_tools() -> None:
    record = make_sharegpt_record(
        user="What is the weather in Shanghai tomorrow?",
        schema={"name": "weather_lookup", "parameters": ["city", "day"]},
        target_call={"name": "weather_lookup", "arguments": {"city": "Shanghai", "day": "tomorrow"}},
    )
    assert record["conversations"][0]["from"] == "human"
    assert record["conversations"][1]["from"] == "function_call"
    assert json.loads(record["tools"])[0]["name"] == "weather_lookup"


def test_build_dataset_info_registers_sharegpt_files() -> None:
    info = build_dataset_info(
        train_files={
            "pilot_v1_vanilla_train": "pilot_v1_vanilla_train.json",
            "pilot_v1_vanilla_eval": "pilot_v1_vanilla_eval.json",
        }
    )
    assert info["pilot_v1_vanilla_train"]["formatting"] == "sharegpt"
    assert info["pilot_v1_vanilla_train"]["columns"]["messages"] == "conversations"
    assert info["pilot_v1_vanilla_train"]["columns"]["tools"] == "tools"


def test_schema_to_tool_preserves_rich_schema_and_normalizes_dict_type() -> None:
    tool = schema_to_tool(
        {
            "name": "math.factorial",
            "description": "Calculate the factorial of a number.",
            "parameters": {
                "type": "dict",
                "properties": {
                    "number": {"type": "long", "description": "The target number."},
                    "flag": {"type": "Boolean", "description": "Boolean flag."},
                },
                "required": ["number", "flag"],
            },
        }
    )
    assert tool["parameters"]["type"] == "object"
    assert tool["parameters"]["properties"]["number"]["type"] == "integer"
    assert tool["parameters"]["properties"]["flag"]["type"] == "boolean"


def test_export_baseline_splits_creates_three_train_datasets() -> None:
    splits = {
        "train": [
            {
                "semantic_task_id": "t1",
                "user": "What is the weather in Shanghai tomorrow?",
                "T_A": {"name": "weather_lookup", "parameters": ["city", "day"]},
                "T_B": {"name": "tool_17", "parameters": ["loc", "date"]},
                "y_A": {"name": "weather_lookup", "arguments": {"city": "Shanghai", "day": "tomorrow"}},
                "y_B": {"name": "tool_17", "arguments": {"loc": "Shanghai", "date": "tomorrow"}},
            }
        ],
        "dev": [],
    }
    exported = export_baseline_splits(splits, irrelevant_tool_count=2)
    assert set(exported["train"]) == {"vanilla", "schema_augmented", "hammer_like"}
    hammer_record = exported["train"]["hammer_like"][0]
    assert len(json.loads(hammer_record["tools"])) == 3


def test_export_baselines_to_directory_reports_empty_eval_split(tmp_path: Path) -> None:
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()

    row = {
        "semantic_task_id": "t1",
        "user": "What is the weather in Shanghai tomorrow?",
        "T_A": {"name": "weather_lookup", "parameters": ["city", "day"]},
        "T_B": {"name": "tool_17", "parameters": ["loc", "date"]},
        "y_A": {"name": "weather_lookup", "arguments": {"city": "Shanghai", "day": "tomorrow"}},
        "y_B": {"name": "tool_17", "arguments": {"loc": "Shanghai", "date": "tomorrow"}},
    }

    (processed_dir / "train.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    (processed_dir / "dev.jsonl").write_text("", encoding="utf-8")
    (processed_dir / "test.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")

    report = export_baselines_to_directory(processed_dir, tmp_path / "exported")

    assert report["dataset_record_counts"]["pilot_v1_vanilla_train"] == 1
    assert report["dataset_record_counts"]["pilot_v1_vanilla_eval"] == 0
    assert "pilot_v1_vanilla_eval" in report["empty_datasets"]
