from __future__ import annotations

from typing import Any

from schema_reuse.models.bottleneck import BottleneckConfig
from schema_reuse.models.reuse_model import ReuseModelConfig
from schema_reuse.train.common import (
    build_common_metrics,
    ensure_run_dir,
    load_dataset_rows,
    resolve_train_config,
    write_json,
    write_predictions,
)


def load_reuse_config(path: str) -> dict[str, Any]:
    config = resolve_train_config(path)
    ReuseModelConfig(
        bottleneck=BottleneckConfig(
            latent_dim=config["latent_dim"],
            enable_reuse=config["enable_reuse"],
            consistency_weight=config.get("consistency_weight", 0.0),
        ),
        cross_schema_weight=config.get("cross_schema_weight", 1.0),
        method_name=config.get("method_name", "reuse_main"),
    )
    return config


class ReuseTrainer:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.model_config = ReuseModelConfig(
            bottleneck=BottleneckConfig(
                latent_dim=config["latent_dim"],
                enable_reuse=config["enable_reuse"],
                consistency_weight=config.get("consistency_weight", 0.0),
            ),
            cross_schema_weight=config.get("cross_schema_weight", 1.0),
            method_name=config.get("method_name", "reuse_main"),
        )

    def run(self, *, max_steps: int = 2) -> str:
        rows = load_dataset_rows(self.config)
        method_name = self.model_config.method_name
        run_dir = ensure_run_dir(self.config["run_root"], method_name, self.config.get("seed", 0))

        predictions = [
            {
                "semantic_task_id": row["semantic_task_id"],
                "status": "smoke_only_no_model",
                "phase": "A_to_B",
                "fixed_d": True,
                "source_schema": row["T_A"],
                "target_schema": row["T_B"],
                "target_call": row["y_B"],
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
                "latent_dim": self.model_config.bottleneck.latent_dim,
                "enable_reuse": self.model_config.bottleneck.enable_reuse,
                "consistency_weight": self.model_config.bottleneck.consistency_weight,
                "cross_schema_weight": self.model_config.cross_schema_weight,
                "fixed_d_objective": True,
            },
        )

        write_json(run_dir / "metrics.json", metrics)
        write_predictions(run_dir / "predictions.jsonl", predictions)
        return str(run_dir)
