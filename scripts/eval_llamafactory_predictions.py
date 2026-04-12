from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import ensure_src_path

ensure_src_path()

from schema_reuse.data.filter_bfcl import load_jsonl
from schema_reuse.eval.counterfactual import write_report
from schema_reuse.eval.toolcall import (
    evaluate_prediction_rows,
    expand_processed_rows_for_mode,
)


def infer_mode_from_path(path: str) -> str | None:
    normalized = path.lower()
    if "schema_augmented" in normalized:
        return "schema_augmented"
    if "hammer_like" in normalized:
        return "hammer_like"
    if "vanilla" in normalized:
        return "vanilla"
    return None


def load_prediction_rows(path: str | Path) -> list[dict]:
    rows: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate exact tool-call correctness from LLaMA-Factory generated_predictions.jsonl."
    )
    parser.add_argument(
        "--predictions",
        required=True,
        help="Path to generated_predictions.jsonl.",
    )
    parser.add_argument(
        "--processed-jsonl",
        default=None,
        help="Optional processed split JSONL used to attach schema/task metadata.",
    )
    parser.add_argument(
        "--mode",
        choices=("vanilla", "schema_augmented", "hammer_like"),
        default=None,
        help="Baseline mode. If omitted, infer from the prediction path.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output report path. Defaults to toolcall_eval.json next to predictions.",
    )
    args = parser.parse_args()

    rows = load_prediction_rows(args.predictions)
    metadata_rows = None
    if args.processed_jsonl:
        mode = args.mode or infer_mode_from_path(args.predictions)
        if mode is None:
            raise SystemExit(
                "Could not infer --mode from prediction path. Pass --mode explicitly."
            )
        metadata_rows = expand_processed_rows_for_mode(load_jsonl(args.processed_jsonl), mode)

    report = evaluate_prediction_rows(rows, metadata_rows=metadata_rows)
    output_path = args.output or str(Path(args.predictions).with_name("toolcall_eval.json"))
    write_report(output_path, metrics=report["metrics"], predictions=report["records"])
    print(json.dumps({"output": output_path, **report["metrics"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
