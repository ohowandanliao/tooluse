from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import ensure_src_path

ensure_src_path()

from schema_reuse.data.filter_bfcl import (
    build_candidate_record,
    is_valid_candidate,
    load_jsonl,
    write_jsonl,
)


def load_config(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_candidate_manifest(config_path: str | Path) -> Path:
    config = load_config(config_path)
    source_rows = load_jsonl(config["input_path"])
    accepted_rows = [
        build_candidate_record(row, source_benchmark=config["source_benchmark"])
        for row in source_rows
        if is_valid_candidate(row)
    ]
    output_path = Path(config["candidate_output_path"])
    write_jsonl(output_path, accepted_rows)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the pilot candidate manifest.")
    parser.add_argument("--config", required=True, help="Path to the pilot data config.")
    args = parser.parse_args()
    output_path = build_candidate_manifest(args.config)
    print(f"Wrote candidate manifest to {output_path}")


if __name__ == "__main__":
    main()
