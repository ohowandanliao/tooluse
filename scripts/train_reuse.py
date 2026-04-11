from __future__ import annotations

import argparse

from _bootstrap import ensure_src_path

ensure_src_path()

from schema_reuse.train.reuse import ReuseTrainer, load_reuse_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-run the fixed-d reuse trainer.")
    parser.add_argument("--config", required=True, help="Path to reuse trainer config.")
    parser.add_argument("--max-steps", type=int, default=2, help="Maximum smoke steps.")
    args = parser.parse_args()

    trainer = ReuseTrainer(load_reuse_config(args.config))
    run_dir = trainer.run(max_steps=args.max_steps)
    print(f"Wrote smoke artifacts to {run_dir}")


if __name__ == "__main__":
    main()
