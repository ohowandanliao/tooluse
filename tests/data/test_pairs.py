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


def test_split_group_id_takes_priority_when_present() -> None:
    rows = [
        {"semantic_task_id": "t1", "split_group_id": "g1"},
        {"semantic_task_id": "t2", "split_group_id": "g1"},
        {"semantic_task_id": "t3", "split_group_id": "g2"},
    ]
    splits = split_candidates(rows, seed=11)
    train_groups = {row["split_group_id"] for row in splits["train"]}
    test_groups = {row["split_group_id"] for row in splits["test"]}
    assert train_groups.isdisjoint(test_groups)
