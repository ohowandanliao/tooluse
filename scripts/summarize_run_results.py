from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CORE_EVIDENCE_FILES = (
    "train_results.json",
    "predict_results.json",
    "toolcall_eval.json",
    "trainer_log.jsonl",
)

TOOLCALL_METRIC_KEYS = (
    "count",
    "parsed_prediction_count",
    "parsed_prediction_rate",
    "exact_match_count",
    "exact_match_rate",
    "name_match_rate",
    "argument_key_exact_match_rate",
    "argument_value_exact_match_rate",
    "exact_match_by_schema_variant",
    "exact_match_by_transform_family",
)

TRAIN_RESULT_KEYS = (
    "epoch",
    "train_loss",
    "train_runtime",
    "train_samples_per_second",
    "train_steps_per_second",
)

PREDICT_RESULT_KEYS = (
    "predict_runtime",
    "predict_samples_per_second",
    "predict_steps_per_second",
    "predict_bleu-4",
    "predict_rouge-1",
    "predict_rouge-2",
    "predict_rouge-l",
)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def select_keys(payload: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {key: payload[key] for key in keys if key in payload}


def infer_mode(run_name: str) -> str | None:
    normalized = run_name.lower()
    if "schema_augmented" in normalized:
        return "schema_augmented"
    if "hammer_like" in normalized:
        return "hammer_like"
    if "vanilla" in normalized:
        return "vanilla"
    return None


def infer_run_kind(run_name: str) -> str:
    if "overfit" in run_name.lower():
        return "sanity_overfit"
    return "baseline"


def infer_config_path(run_name: str) -> str | None:
    normalized = run_name.lower()
    prefix = "configs/llamafactory/"

    if "qwen25_05b_schema_augmented_qlora_pilot1000" in normalized:
        return (
            f"{prefix}"
            "local_qwen25_05b_xlam_fc_single_call_schema_augmented_qlora_pilot1000.yaml"
        )
    if "qwen25_05b_hammer_like_qlora_pilot1000" in normalized:
        return (
            f"{prefix}"
            "local_qwen25_05b_xlam_fc_single_call_hammer_like_qlora_pilot1000.yaml"
        )
    if "qwen25_05b_vanilla_qlora_pilot1000" in normalized:
        return f"{prefix}local_qwen25_05b_xlam_fc_single_call_vanilla_qlora_pilot1000.yaml"
    if "qwen25_05b_vanilla_overfit_trainbook_qlora" in normalized:
        return f"{prefix}local_qwen25_05b_vanilla_overfit_trainbook_qlora.yaml"
    if "qwen25_05b_schema_augmented_qlora" in normalized:
        return f"{prefix}local_qwen25_05b_schema_augmented_qlora.yaml"
    if "qwen25_05b_hammer_like_qlora" in normalized:
        return f"{prefix}local_qwen25_05b_hammer_like_qlora.yaml"
    if "qwen25_05b_vanilla_qlora" in normalized:
        return f"{prefix}local_qwen25_05b_vanilla_qlora.yaml"
    return None


def infer_conclusion(toolcall_metrics: dict[str, Any], run_kind: str) -> str:
    exact_match_rate = toolcall_metrics.get("exact_match_rate")
    name_match_rate = toolcall_metrics.get("name_match_rate")
    argument_key_rate = toolcall_metrics.get("argument_key_exact_match_rate")
    argument_value_rate = toolcall_metrics.get("argument_value_exact_match_rate")

    if run_kind == "sanity_overfit" and exact_match_rate == 1.0:
        return "Overfit sanity pass; the train-export-predict-eval stack is connected."
    if (
        exact_match_rate == 0.0
        and name_match_rate == 1.0
        and argument_key_rate == 1.0
        and argument_value_rate == 0.0
    ):
        return "Tool name and argument keys are correct, but argument values fail exact match."
    if exact_match_rate == 1.0:
        return "Exact tool-call match reached 100% on this slice."
    if exact_match_rate is None:
        return "Tool-call report missing; inspect the external run directory."
    return "See the repo evidence bundle and external run directory for details."


def evidence_file_names(*, include_generated_predictions: bool) -> tuple[str, ...]:
    if include_generated_predictions:
        return CORE_EVIDENCE_FILES + ("generated_predictions.jsonl",)
    return CORE_EVIDENCE_FILES


def copy_evidence_files(
    run_dir: Path,
    bundle_dir: Path,
    *,
    include_generated_predictions: bool,
) -> list[str]:
    copied: list[str] = []
    bundle_dir.mkdir(parents=True, exist_ok=True)

    for name in evidence_file_names(
        include_generated_predictions=include_generated_predictions
    ):
        source = run_dir / name
        if source.exists():
            shutil.copy2(source, bundle_dir / name)
            copied.append(name)

    return copied


def summarize_run(
    run_dir: Path,
    bundle_dir: Path,
    *,
    include_generated_predictions: bool,
) -> dict[str, Any]:
    toolcall_path = run_dir / "toolcall_eval.json"
    train_path = run_dir / "train_results.json"
    predict_path = run_dir / "predict_results.json"

    toolcall_report = read_json(toolcall_path) if toolcall_path.exists() else {}
    train_results = read_json(train_path) if train_path.exists() else {}
    predict_results = read_json(predict_path) if predict_path.exists() else {}
    toolcall_metrics = select_keys(toolcall_report.get("metrics", {}), TOOLCALL_METRIC_KEYS)
    copied_files = copy_evidence_files(
        run_dir,
        bundle_dir,
        include_generated_predictions=include_generated_predictions,
    )

    return {
        "run_name": run_dir.name,
        "mode": infer_mode(run_dir.name),
        "run_kind": infer_run_kind(run_dir.name),
        "config_path": infer_config_path(run_dir.name),
        "artifact_path": str(run_dir),
        "repo_bundle_path": str(bundle_dir),
        "copied_evidence_files": copied_files,
        "metrics": {
            "toolcall": toolcall_metrics,
            "train": select_keys(train_results, TRAIN_RESULT_KEYS),
            "predict": select_keys(predict_results, PREDICT_RESULT_KEYS),
        },
        "conclusion": infer_conclusion(toolcall_metrics, infer_run_kind(run_dir.name)),
    }


def build_manifest(
    run_root: Path,
    output_dir: Path,
    *,
    machine: str | None,
    experiment_group: str | None,
    dataset: str | None,
    include_generated_predictions: bool,
) -> dict[str, Any]:
    run_dirs = sorted(path for path in run_root.iterdir() if path.is_dir())
    runs = [
        summarize_run(
            run_dir,
            output_dir / run_dir.name,
            include_generated_predictions=include_generated_predictions,
        )
        for run_dir in run_dirs
    ]

    best_run = None
    if runs:
        best_run = max(
            runs,
            key=lambda run: run["metrics"]["toolcall"].get("exact_match_rate", -1.0),
        )

    return {
        "schema_version": 1,
        "generated_at_utc": (
            datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        ),
        "machine": machine,
        "experiment_group": experiment_group,
        "dataset": dataset,
        "artifact_root": str(run_root),
        "repo_bundle_root": str(output_dir),
        "include_generated_predictions": include_generated_predictions,
        "run_count": len(runs),
        "runs": runs,
        "summary": {
            "best_exact_match_run": None if best_run is None else best_run["run_name"],
            "best_exact_match_rate": None
            if best_run is None
            else best_run["metrics"]["toolcall"].get("exact_match_rate"),
            "repo_policy": (
                "Commit lightweight experiment evidence here, but keep weights and other heavy artifacts outside the repo."
            ),
        },
    }


def materialize_results_bundle(
    run_root: Path,
    output_dir: Path,
    *,
    machine: str | None,
    experiment_group: str | None,
    dataset: str | None,
    include_generated_predictions: bool,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest(
        run_root,
        output_dir,
        machine=machine,
        experiment_group=experiment_group,
        dataset=dataset,
        include_generated_predictions=include_generated_predictions,
    )
    manifest_path = output_dir / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Copy lightweight run evidence into the repo and write a summary manifest."
    )
    parser.add_argument(
        "--run-root",
        required=True,
        help="Directory containing external per-run output folders.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Repo directory that will receive manifest.json and per-run evidence subdirectories.",
    )
    parser.add_argument(
        "--machine",
        default=None,
        help="Optional machine label, for example local_2080ti.",
    )
    parser.add_argument(
        "--experiment-group",
        default=None,
        help="Optional experiment group label, for example pilot_v1.",
    )
    parser.add_argument(
        "--dataset",
        default=None,
        help="Optional dataset label recorded in the manifest.",
    )
    parser.add_argument(
        "--include-generated-predictions",
        action="store_true",
        help="Also copy generated_predictions.jsonl into each repo evidence bundle.",
    )
    args = parser.parse_args()

    run_root = Path(args.run_root)
    if not run_root.exists():
        raise SystemExit(f"Run root does not exist: {run_root}")

    manifest = materialize_results_bundle(
        run_root,
        Path(args.output_dir),
        machine=args.machine,
        experiment_group=args.experiment_group,
        dataset=args.dataset,
        include_generated_predictions=args.include_generated_predictions,
    )

    print(
        json.dumps(
            {
                "output_dir": args.output_dir,
                "manifest": f"{args.output_dir}/manifest.json",
                "run_count": manifest["run_count"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
