from schema_reuse.data.pairs import split_candidates


def test_semantic_task_ids_do_not_cross_splits() -> None:
    rows = [
        {"semantic_task_id": "t1"},
        {"semantic_task_id": "t1"},
        {"semantic_task_id": "t2"},
    ]
    splits = split_candidates(rows, seed=11)
    train_ids = {row["semantic_task_id"] for row in splits["train"]}
    test_ids = {row["semantic_task_id"] for row in splits["test"]}
    assert train_ids.isdisjoint(test_ids)
