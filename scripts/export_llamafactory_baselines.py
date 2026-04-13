from __future__ import annotations

import argparse
import json

from _bootstrap import ensure_src_path

ensure_src_path()

from schema_reuse.export.llamafactory import export_baselines_to_directory


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export pilot-v1 baseline datasets for LLaMA-Factory CLI."
    )
    parser.add_argument(
        "--processed-dir",
        default="data/processed/pilot_v1",
        help="Directory containing processed train/dev/test JSONL files.",
    )
    parser.add_argument(
        "--output-dir",
        default="data/llamafactory/pilot_v1",
        help="Directory to write exported JSON datasets and dataset_info.json.",
    )
    parser.add_argument(
        "--irrelevant-tool-count",
        type=int,
        default=2,
        help="Number of irrelevant tools to inject for hammer_like exports.",
    )
    parser.add_argument(
        "--dataset-prefix",
        default="pilot_v1",
        help="Dataset prefix used for exported dataset names.",
    )
    args = parser.parse_args()

    report = export_baselines_to_directory(
        args.processed_dir,
        args.output_dir,
        irrelevant_tool_count=args.irrelevant_tool_count,
        dataset_prefix=args.dataset_prefix,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
