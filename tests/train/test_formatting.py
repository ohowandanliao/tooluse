from schema_reuse.train.formatting import (
    build_direct_example,
    build_reuse_example,
    serialize_call,
)


def test_serialize_call_is_stable_json() -> None:
    call = {"name": "weather_lookup", "arguments": {"city": "Shanghai", "day": "tomorrow"}}
    text = serialize_call(call)
    assert '"name":"weather_lookup"' in text
    assert '"city":"Shanghai"' in text


def test_build_direct_example_mentions_schema_and_target() -> None:
    row = {
        "user": "What is the weather in Shanghai tomorrow?",
        "T_A": {"name": "weather_lookup", "parameters": ["city", "day"]},
        "y_A": {"name": "weather_lookup", "arguments": {"city": "Shanghai", "day": "tomorrow"}},
    }
    example = build_direct_example(row, schema_key="T_A", target_key="y_A")
    assert "Schema:" in example["prompt"]
    assert "weather_lookup" in example["target"]


def test_build_reuse_example_mentions_source_and_target_schema() -> None:
    row = {
        "user": "What is the weather in Shanghai tomorrow?",
        "T_A": {"name": "weather_lookup", "parameters": ["city", "day"]},
        "T_B": {"name": "tool_17", "parameters": ["loc", "date"]},
        "y_B": {"name": "tool_17", "arguments": {"loc": "Shanghai", "date": "tomorrow"}},
    }
    example = build_reuse_example(row)
    assert "Source Schema" in example["prompt"]
    assert "Target Schema" in example["prompt"]
    assert "tool_17" in example["target"]
