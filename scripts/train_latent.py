from __future__ import annotations

import argparse

from _bootstrap import ensure_src_path

ensure_src_path()

from schema_reuse.train.latent import LatentTrainer, load_latent_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-run latent baselines.")
    parser.add_argument("--config", required=True, help="Path to latent baseline config.")
    parser.add_argument("--max-steps", type=int, default=2, help="Maximum smoke steps.")
    args = parser.parse_args()

    trainer = LatentTrainer(load_latent_config(args.config))
    run_dir = trainer.run(max_steps=args.max_steps)
    print(f"Wrote smoke artifacts to {run_dir}")


if __name__ == "__main__":
    main()
