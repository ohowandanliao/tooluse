from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from _bootstrap import ensure_src_path

ensure_src_path()

from schema_reuse.data.bfcl_official import (
    build_bfcl_sample,
    build_split_group_id,
    load_jsonl_by_id,
    resolve_env_path,
)
from schema_reuse.data.filter_bfcl import build_candidate_record, candidate_audit, write_jsonl


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
    accepted_rows: list[dict[str, Any]] = []
    total_rejection_reasons: Counter[str] = Counter()
    category_reports: list[dict[str, Any]] = []

    split_group_strategy = config.get("split_group_strategy", "semantic_task")
    require_single_tool = bool(config.get("require_single_tool", True))

    for category in config["categories"]:
        category_name = category["name"]
        question_path = resolve_env_path(category["question_path"])
        answer_path = resolve_env_path(category["answer_path"])
        question_rows = load_jsonl_by_id(question_path)
        answer_rows = load_jsonl_by_id(answer_path)
        category_rejection_reasons: Counter[str] = Counter()
        category_accepted = 0

        for row_id in sorted(question_rows):
            if row_id not in answer_rows:
                category_rejection_reasons["missing_answer"] += 1
                total_rejection_reasons["missing_answer"] += 1
                continue

            try:
                sample = build_bfcl_sample(
                    question_rows[row_id],
                    answer_rows[row_id],
                    category_name=category_name,
                    source_benchmark=config["source_benchmark"],
                    language=category.get("language"),
                    require_single_tool=require_single_tool,
                )
            except ValueError as exc:
                reason = str(exc)
                category_rejection_reasons[reason] += 1
                total_rejection_reasons[reason] += 1
                continue

            audit = candidate_audit(sample)
            if not audit["is_valid"]:
                reason = str(audit["reason"])
                category_rejection_reasons[reason] += 1
                total_rejection_reasons[reason] += 1
                continue

            split_group_id = build_split_group_id(sample, strategy=split_group_strategy)
            accepted_rows.append(
                build_candidate_record(
                    sample,
                    source_benchmark=config["source_benchmark"],
                    split_group_id=split_group_id,
                )
            )
            category_accepted += 1

        orphan_answers = sorted(set(answer_rows) - set(question_rows))
        if orphan_answers:
            category_rejection_reasons["orphan_answer"] += len(orphan_answers)
            total_rejection_reasons["orphan_answer"] += len(orphan_answers)

        category_reports.append(
            {
                "name": category_name,
                "language": category.get("language"),
                "question_path": str(question_path),
                "answer_path": str(answer_path),
                "raw_question_count": len(question_rows),
                "raw_answer_count": len(answer_rows),
                "accepted_count": category_accepted,
                "rejected_count": sum(category_rejection_reasons.values()),
                "rejection_reasons": dict(category_rejection_reasons),
            }
        )

    candidate_output_path = Path(config["candidate_output_path"])
    write_jsonl(candidate_output_path, accepted_rows)

    accepted_categories = Counter(
        row.get("metadata", {}).get("bfcl_category", "unknown")
        for row in accepted_rows
    )
    accepted_languages = Counter(
        row.get("metadata", {}).get("language", "unknown")
        for row in accepted_rows
    )
    unique_tools = sorted({row["ground_truth"]["name"] for row in accepted_rows})
    unique_split_groups = len({row.get("split_group_id") for row in accepted_rows})

    report = {
        "config_path": str(config_path),
        "source_benchmark": config["source_benchmark"],
        "split_group_strategy": split_group_strategy,
        "require_single_tool": require_single_tool,
        "candidate_output_path": str(candidate_output_path),
        "category_reports": category_reports,
        "summary": {
            "accepted_candidate_count": len(accepted_rows),
            "rejected_count": sum(total_rejection_reasons.values()),
            "rejection_reasons": dict(total_rejection_reasons),
            "accepted_categories": dict(accepted_categories),
            "accepted_languages": dict(accepted_languages),
            "unique_tool_count": len(unique_tools),
            "unique_split_group_count": unique_split_groups,
        },
    }

    audit_report_path = Path(config["audit_report_path"])
    _write_json(audit_report_path, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a BFCL v4 single-turn single-tool candidate manifest."
    )
    parser.add_argument("--config", required=True, help="Path to the BFCL slice config.")
    args = parser.parse_args()

    report = build_candidate_manifest(args.config)
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2, sort_keys=True))
    print(f"audit_report_path={Path(load_config(args.config)['audit_report_path'])}")


if __name__ == "__main__":
    main()
