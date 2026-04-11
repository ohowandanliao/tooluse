from schema_reuse.data.filter_bfcl import is_valid_candidate


def test_rejects_explicit_tool_mentions() -> None:
    sample = {"user": "call weather_lookup for Shanghai", "tools": ["weather_lookup"]}
    assert is_valid_candidate(sample) is False


def test_accepts_single_turn_executable_call() -> None:
    sample = {
        "user": "What is the weather in Shanghai tomorrow?",
        "ground_truth": {"name": "opaque_a", "arguments": {"city": "Shanghai", "day": "tomorrow"}},
        "metadata": {"single_turn": True, "ast_verifiable": True},
    }
    assert is_valid_candidate(sample) is True
