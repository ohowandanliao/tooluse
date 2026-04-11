from __future__ import annotations

import argparse

from _bootstrap import ensure_src_path

ensure_src_path()

from schema_reuse.train.direct import DirectTrainer, load_train_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-run direct baselines.")
    parser.add_argument("--config", required=True, help="Path to direct baseline config.")
    parser.add_argument("--mode", required=True, help="Direct baseline mode to run.")
    parser.add_argument("--max-steps", type=int, default=2, help="Maximum smoke steps.")
    args = parser.parse_args()

    trainer = DirectTrainer(load_train_config(args.config))
    run_dir = trainer.run(mode=args.mode, max_steps=args.max_steps)
    print(f"Wrote smoke artifacts to {run_dir}")


if __name__ == "__main__":
    main()
