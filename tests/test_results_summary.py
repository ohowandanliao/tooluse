from __future__ import annotations

import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "summarize_run_results.py"
SPEC = importlib.util.spec_from_file_location("summarize_run_results", SCRIPT_PATH)
assert SPEC is not None
assert SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_materialize_results_bundle_copies_evidence_and_writes_manifest(
    tmp_path: Path,
) -> None:
    run_root = tmp_path / "external_runs"
    output_dir = tmp_path / "results_bundle"

    vanilla_dir = run_root / "qwen25_05b_vanilla_qlora"
    write_json(
        vanilla_dir / "toolcall_eval.json",
        {
            "metrics": {
                "count": 1,
                "parsed_prediction_count": 1,
                "parsed_prediction_rate": 1.0,
                "exact_match_count": 0,
                "exact_match_rate": 0.0,
                "name_match_rate": 1.0,
                "argument_key_exact_match_rate": 1.0,
                "argument_value_exact_match_rate": 0.0,
            },
            "predictions": [],
        },
    )
    write_json(
        vanilla_dir / "train_results.json",
        {
            "epoch": 30.0,
            "train_loss": 0.0014,
            "train_runtime": 25.3,
            "train_samples_per_second": 1.18,
            "train_steps_per_second": 1.18,
        },
    )
    write_json(
        vanilla_dir / "predict_results.json",
        {
            "predict_runtime": 8.6,
            "predict_samples_per_second": 0.11,
            "predict_steps_per_second": 0.11,
            "predict_bleu-4": 97.8,
        },
    )
    (vanilla_dir / "trainer_log.jsonl").write_text('{"loss": 0.1}\n', encoding="utf-8")
    (vanilla_dir / "generated_predictions.jsonl").write_text(
        '{"predict":"<tool_call>{}</tool_call>"}\n',
        encoding="utf-8",
    )

    overfit_dir = run_root / "qwen25_05b_vanilla_overfit_trainbook_qlora"
    write_json(
        overfit_dir / "toolcall_eval.json",
        {
            "metrics": {
                "count": 1,
                "parsed_prediction_count": 1,
                "parsed_prediction_rate": 1.0,
                "exact_match_count": 1,
                "exact_match_rate": 1.0,
                "name_match_rate": 1.0,
                "argument_key_exact_match_rate": 1.0,
                "argument_value_exact_match_rate": 1.0,
            },
            "predictions": [],
        },
    )
    write_json(
        overfit_dir / "train_results.json",
        {
            "epoch": 40.0,
            "train_loss": 0.02,
            "train_runtime": 19.7,
            "train_samples_per_second": 2.0,
            "train_steps_per_second": 2.0,
        },
    )
    write_json(
        overfit_dir / "predict_results.json",
        {
            "predict_runtime": 3.8,
            "predict_samples_per_second": 0.26,
            "predict_steps_per_second": 0.26,
            "predict_bleu-4": 99.1,
        },
    )
    (overfit_dir / "trainer_log.jsonl").write_text('{"loss": 0.02}\n', encoding="utf-8")
    (overfit_dir / "generated_predictions.jsonl").write_text(
        '{"predict":"<tool_call>{}</tool_call>"}\n',
        encoding="utf-8",
    )

    manifest = MODULE.materialize_results_bundle(
        run_root,
        output_dir,
        machine="local_2080ti",
        experiment_group="pilot_v1",
        dataset="pilot_v1",
        include_generated_predictions=True,
    )

    assert manifest["machine"] == "local_2080ti"
    assert manifest["experiment_group"] == "pilot_v1"
    assert manifest["dataset"] == "pilot_v1"
    assert manifest["run_count"] == 2
    assert manifest["summary"]["best_exact_match_run"] == "qwen25_05b_vanilla_overfit_trainbook_qlora"
    assert manifest["summary"]["best_exact_match_rate"] == 1.0

    vanilla_summary = next(run for run in manifest["runs"] if run["run_name"] == "qwen25_05b_vanilla_qlora")
    assert vanilla_summary["mode"] == "vanilla"
    assert vanilla_summary["run_kind"] == "baseline"
    assert vanilla_summary["config_path"] == "configs/llamafactory/local_qwen25_05b_vanilla_qlora.yaml"
    assert vanilla_summary["metrics"]["toolcall"]["exact_match_rate"] == 0.0
    assert "argument values fail exact match" in vanilla_summary["conclusion"]
    assert "generated_predictions.jsonl" in vanilla_summary["copied_evidence_files"]

    overfit_summary = next(
        run for run in manifest["runs"] if run["run_name"] == "qwen25_05b_vanilla_overfit_trainbook_qlora"
    )
    assert overfit_summary["run_kind"] == "sanity_overfit"
    assert overfit_summary["config_path"] == (
        "configs/llamafactory/local_qwen25_05b_vanilla_overfit_trainbook_qlora.yaml"
    )
    assert overfit_summary["metrics"]["toolcall"]["exact_match_rate"] == 1.0
    assert "Overfit sanity pass" in overfit_summary["conclusion"]

    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "qwen25_05b_vanilla_qlora" / "trainer_log.jsonl").exists()
    assert (output_dir / "qwen25_05b_vanilla_qlora" / "generated_predictions.jsonl").exists()


def test_infer_config_path_supports_xlam_pilot_configs() -> None:
    assert MODULE.infer_config_path("qwen25_05b_vanilla_qlora_pilot1000") == (
        "configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_vanilla_qlora_pilot1000.yaml"
    )
    assert MODULE.infer_config_path("qwen25_05b_schema_augmented_qlora_pilot1000") == (
        "configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_schema_augmented_qlora_pilot1000.yaml"
    )
    assert MODULE.infer_config_path("qwen25_05b_hammer_like_qlora_pilot1000") == (
        "configs/llamafactory/local_qwen25_05b_xlam_fc_single_call_hammer_like_qlora_pilot1000.yaml"
    )
