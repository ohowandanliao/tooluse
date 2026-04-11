from __future__ import annotations

import argparse

from _bootstrap import ensure_src_path

ensure_src_path()

from schema_reuse.data.pairs import build_processed_datasets, load_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the paired pilot dataset.")
    parser.add_argument("--config", required=True, help="Path to the pilot data config.")
    args = parser.parse_args()

    written_paths = build_processed_datasets(load_config(args.config))
    for split_name, path in written_paths.items():
        print(f"{split_name}: {path}")


if __name__ == "__main__":
    main()
