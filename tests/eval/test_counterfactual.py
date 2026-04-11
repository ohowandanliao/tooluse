from schema_reuse.eval.counterfactual import compute_counterfactual_metrics


def test_counterfactual_report_has_required_keys() -> None:
    report = compute_counterfactual_metrics(
        a_to_a=[1, 0],
        b_to_b=[1, 1],
        a_to_b=[1, 0],
        shuffle=[0, 0],
        null=[0, 0],
    )
    assert set(report) >= {
        "A_to_A_exec_acc",
        "B_to_B_exec_acc",
        "A_to_B_exec_acc",
        "shuffle_exec_acc",
        "null_exec_acc",
        "cf_gap",
    }
