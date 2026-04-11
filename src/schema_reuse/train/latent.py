from __future__ import annotations

from typing import Any

from schema_reuse.models.bottleneck import BottleneckConfig
from schema_reuse.train.common import (
    build_common_metrics,
    ensure_run_dir,
    load_dataset_rows,
    resolve_train_config,
    write_json,
    write_predictions,
)


def load_latent_config(path: str) -> dict[str, Any]:
    config = resolve_train_config(path)
    BottleneckConfig(
        latent_dim=config["latent_dim"],
        enable_reuse=config.get("enable_reuse", False),
        consistency_weight=config.get("consistency_weight", 0.0),
    )
    return config


class LatentTrainer:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.bottleneck = BottleneckConfig(
            latent_dim=config["latent_dim"],
            enable_reuse=config.get("enable_reuse", False),
            consistency_weight=config.get("consistency_weight", 0.0),
        )

    def run(self, *, max_steps: int = 2) -> str:
        rows = load_dataset_rows(self.config)
        method_name = self.config["method_name"]
        run_dir = ensure_run_dir(self.config["run_root"], method_name, self.config.get("seed", 0))

        predictions = [
            {
                "semantic_task_id": row["semantic_task_id"],
                "status": "smoke_only_no_model",
                "latent_dim": self.bottleneck.latent_dim,
                "target_call": row["y_A"],
                "predicted_call": None,
            }
            for row in rows[: max(1, min(max_steps, len(rows)))]
        ]

        metrics = build_common_metrics(
            self.config,
            method_name=method_name,
            max_steps=max_steps,
            num_examples=len(rows),
            extra_metrics={
                "latent_dim": self.bottleneck.latent_dim,
                "enable_reuse": self.bottleneck.enable_reuse,
                "consistency_weight": self.bottleneck.consistency_weight,
            },
        )

        write_json(run_dir / "metrics.json", metrics)
        write_predictions(run_dir / "predictions.jsonl", predictions)
        return str(run_dir)
