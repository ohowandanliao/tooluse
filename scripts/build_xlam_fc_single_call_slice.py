from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from _bootstrap import ensure_src_path

ensure_src_path()

from schema_reuse.data.bfcl_official import build_split_group_id
from schema_reuse.data.filter_bfcl import build_candidate_record, candidate_audit, write_jsonl
from schema_reuse.data.xlam_official import build_xlam_sample, load_xlam_rows


def load_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: str | Path, payload: Any) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)


def build_candidate_manifest(config_path: str | Path) -> dict[str, Any]:
    config = load_config(config_path)
    rows = load_xlam_rows(config["input_path"])
    accepted_rows: list[dict[str, Any]] = []
    rejection_reasons: Counter[str] = Counter()

    split_group_strategy = config.get("split_group_strategy", "semantic_task")
    require_single_answer = bool(config.get("require_single_answer", True))

    for row in rows:
        try:
            sample = build_xlam_sample(
                row,
                source_benchmark=config["source_benchmark"],
                require_single_answer=require_single_answer,
            )
        except ValueError as exc:
            rejection_reasons[str(exc)] += 1
            continue

        audit = candidate_audit(sample)
        if not audit["is_valid"]:
            rejection_reasons[str(audit["reason"])] += 1
            continue

        split_group_id = build_split_group_id(sample, strategy=split_group_strategy)
        accepted_rows.append(
            build_candidate_record(
                sample,
                source_benchmark=config["source_benchmark"],
                split_group_id=split_group_id,
            )
        )

    candidate_output_path = Path(config["candidate_output_path"])
    write_jsonl(candidate_output_path, accepted_rows)

    unique_tools = sorted({row["ground_truth"]["name"] for row in accepted_rows})
    unique_split_groups = len({row["split_group_id"] for row in accepted_rows})
    report = {
        "config_path": str(config_path),
        "input_path": str(config["input_path"]),
        "source_benchmark": config["source_benchmark"],
        "split_group_strategy": split_group_strategy,
        "require_single_answer": require_single_answer,
        "candidate_output_path": str(candidate_output_path),
        "summary": {
            "raw_row_count": len(rows),
            "accepted_candidate_count": len(accepted_rows),
            "rejected_count": sum(rejection_reasons.values()),
            "rejection_reasons": dict(rejection_reasons),
            "unique_tool_count": len(unique_tools),
            "unique_split_group_count": unique_split_groups,
        },
    }

    _write_json(config["audit_report_path"], report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build an xLAM function-calling single-call candidate manifest."
    )
    parser.add_argument("--config", required=True, help="Path to the xLAM slice config.")
    args = parser.parse_args()

    report = build_candidate_manifest(args.config)
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2, sort_keys=True))
    print(f"audit_report_path={Path(load_config(args.config)['audit_report_path'])}")


if __name__ == "__main__":
    main()
