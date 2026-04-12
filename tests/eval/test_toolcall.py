from schema_reuse.eval.toolcall import (
    evaluate_prediction_rows,
    expand_processed_rows_for_mode,
    parse_tool_call,
)


def test_parse_tool_call_reads_xml_wrapped_payload() -> None:
    parsed = parse_tool_call(
        "<tool_call>\n"
        '{"name":"train_book","arguments":{"arrival_city":"Hangzhou","departure_city":"Beijing"}}\n'
        "</tool_call>"
    )
    assert parsed == {
        "name": "train_book",
        "arguments": {
            "arrival_city": "Hangzhou",
            "departure_city": "Beijing",
        },
    }


def test_evaluate_prediction_rows_reports_exact_and_grouped_metrics() -> None:
    rows = [
        {
            "prompt": "prompt-a",
            "predict": (
                "<tool_call>\n"
                '{"name":"train_book","arguments":{"arrival_city":"Hangzhou","departure_city":"Beijing"}}\n'
                "</tool_call>"
            ),
            "label": (
                "<tool_call>\n"
                '{"name":"train_book","arguments":{"arrival_city":"Hangzhou","departure_city":"Beijing"}}\n'
                "</tool_call>"
            ),
        },
        {
            "prompt": "prompt-b",
            "predict": (
                "<tool_call>\n"
                '{"name":"test_tool_0000","arguments":{"test_arg_0000":"北京","test_arg_0001":"杭州"}}\n'
                "</tool_call>"
            ),
            "label": (
                "<tool_call>\n"
                '{"name":"test_tool_0000","arguments":{"test_arg_0000":"Beijing","test_arg_0001":"Hangzhou"}}\n'
                "</tool_call>"
            ),
        },
    ]
    metadata = [
        {"schema_variant": "A", "transform_family": "rename_arg_reorder"},
        {"schema_variant": "B", "transform_family": "rename_arg_reorder"},
    ]

    report = evaluate_prediction_rows(rows, metadata_rows=metadata)

    assert report["metrics"]["count"] == 2
    assert report["metrics"]["exact_match_count"] == 1
    assert report["metrics"]["exact_match_rate"] == 0.5
    assert report["metrics"]["name_match_rate"] == 1.0
    assert report["metrics"]["argument_key_exact_match_rate"] == 1.0
    assert report["metrics"]["argument_value_exact_match_rate"] == 0.5
    assert report["metrics"]["exact_match_by_schema_variant"] == {"A": 1.0, "B": 0.0}


def test_expand_processed_rows_for_schema_augmented_tracks_a_and_b() -> None:
    rows = [
        {
            "T_A": {"name": "train_book", "parameters": ["arrival_city", "departure_city"]},
            "T_B": {"name": "test_tool_0000", "parameters": ["test_arg_0001", "test_arg_0000"]},
            "y_A": {
                "name": "train_book",
                "arguments": {"arrival_city": "Hangzhou", "departure_city": "Beijing"},
            },
            "y_B": {
                "name": "test_tool_0000",
                "arguments": {"test_arg_0000": "Beijing", "test_arg_0001": "Hangzhou"},
            },
            "alias_split": "test",
            "semantic_task_id": "task_079d92a155ae",
            "source_benchmark": "toy_seed",
            "transform_family": "rename_arg_reorder",
            "user": "Book me a train from Beijing to Hangzhou.",
        }
    ]

    expanded = expand_processed_rows_for_mode(rows, "schema_augmented")

    assert len(expanded) == 2
    assert expanded[0]["schema_variant"] == "A"
    assert expanded[1]["schema_variant"] == "B"
    assert expanded[0]["expected_tool_name"] == "train_book"
    assert expanded[1]["expected_tool_name"] == "test_tool_0000"
