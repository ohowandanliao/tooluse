from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import ensure_src_path

ensure_src_path()

from schema_reuse.eval.counterfactual import (
    compute_counterfactual_metrics,
    compute_track_p_metrics,
    write_report,
)


def load_config(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate counterfactual decoding outputs.")
    parser.add_argument("--run-dir", required=False, help="Directory containing model outputs.")
    parser.add_argument("--dataset-path", required=False, help="Path to processed dataset JSONL.")
    parser.add_argument("--decode-config", required=True, help="Path to decode config.")
    parser.add_argument(
        "--mode",
        choices=("track_r", "track_p"),
        default=None,
        help="Evaluation mode.",
    )
    parser.add_argument(
        "--output",
        required=False,
        default="runs/pilot_v1/eval_stub/report.json",
        help="Where to write the aggregated report.",
    )
    args = parser.parse_args()

    config = load_config(args.decode_config)
    mode = args.mode or config.get("default_track", "track_r")

    if mode == "track_r":
        metrics = compute_counterfactual_metrics(
            a_to_a=[],
            b_to_b=[],
            a_to_b=[],
            shuffle=[],
            null=[],
        )
    else:
        metrics = compute_track_p_metrics(
            heldout_exec=[],
            heldout_ast=[],
            transform_families=[],
        )

    write_report(args.output, metrics=metrics, predictions=[])
    print(f"Wrote {mode} report to {args.output}")


if __name__ == "__main__":
    main()
