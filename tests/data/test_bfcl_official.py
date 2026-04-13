from schema_reuse.data.bfcl_official import (
    build_bfcl_sample,
    build_split_group_id,
    canonicalize_ground_truth,
)


def test_canonicalize_ground_truth_omits_blank_optional_argument() -> None:
    call, metadata = canonicalize_ground_truth(
        [{"weather_lookup": {"city": ["Shanghai"], "unit": ["metric", ""]}}]
    )
    assert call == {"name": "weather_lookup", "arguments": {"city": "Shanghai"}}
    assert metadata["omitted_optional_arguments"] == ["unit"]


def test_build_bfcl_sample_extracts_single_turn_tool_spec() -> None:
    question_row = {
        "id": "simple_python_0",
        "question": [[{"role": "user", "content": "Calculate the factorial of 5."}]],
        "function": [
            {
                "name": "math.factorial",
                "description": "Calculate the factorial of a number.",
                "parameters": {
                    "type": "dict",
                    "properties": {
                        "number": {
                            "type": "integer",
                            "description": "The number to evaluate.",
                        }
                    },
                    "required": ["number"],
                },
            }
        ],
    }
    answer_row = {
        "id": "simple_python_0",
        "ground_truth": [{"math.factorial": {"number": [5]}}],
    }

    sample = build_bfcl_sample(
        question_row,
        answer_row,
        category_name="simple_python",
        source_benchmark="bfcl_v4_single_turn_single_tool",
        language="python",
    )

    assert sample["user"] == "Calculate the factorial of 5."
    assert sample["ground_truth"] == {
        "name": "math.factorial",
        "arguments": {"number": 5},
    }
    assert sample["tool_spec"]["name"] == "math.factorial"
    assert sample["metadata"]["bfcl_category"] == "simple_python"
    assert sample["metadata"]["num_tools"] == 1


def test_split_group_id_can_group_by_tool_signature() -> None:
    sample = {
        "ground_truth": {
            "name": "math.factorial",
            "arguments": {"number": 5},
        },
        "tool_pool_spec": [
            {
                "name": "math.factorial",
                "parameters": {"properties": {"number": {"type": "integer"}}},
            }
        ],
        "metadata": {"bfcl_category": "simple_python"},
    }
    group_id = build_split_group_id(sample, strategy="tool_signature")
    assert group_id.startswith("group_")
