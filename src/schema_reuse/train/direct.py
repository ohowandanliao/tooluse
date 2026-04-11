from __future__ import annotations

import random
from copy import deepcopy
from typing import Any

from schema_reuse.models.direct_fc import DirectFCConfig
from schema_reuse.models.hammer_like import inject_irrelevant_tools, mask_schema_name
from schema_reuse.train.common import (
    build_common_metrics,
    ensure_run_dir,
    load_dataset_rows,
    resolve_train_config,
    write_json,
    write_predictions,
)


def load_train_config(path: str) -> dict[str, Any]:
    config = resolve_train_config(path)
    DirectFCConfig(
        mode=config["mode"],
        backbone_model_id=config["backbone_model_id"],
        name_mask_probability=config.get("name_mask_probability", 0.0),
        irrelevant_tool_count=config.get("irrelevant_tool_count", 0),
    )
    return config


class DirectTrainer:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    def _build_views(self, rows: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
        rng = random.Random(self.config.get("seed", 0))
        views: list[dict[str, Any]] = []
        include_target_schema = mode in {"schema_augmented_sft", "hammer_like"}

        for row in rows:
            base_view = {
                "semantic_task_id": row["semantic_task_id"],
                "user": row["user"],
                "presented_schema": deepcopy(row["T_A"]),
                "target_call": deepcopy(row["y_A"]),
                "variant": "A",
            }
            views.append(base_view)

            if include_target_schema:
                augmented_view = {
                    "semantic_task_id": row["semantic_task_id"],
                    "user": row["user"],
                    "presented_schema": deepcopy(row["T_B"]),
                    "target_call": deepcopy(row["y_B"]),
                    "variant": "B",
                }
                views.append(augmented_view)

        if mode == "hammer_like":
            masked_views: list[dict[str, Any]] = []
            for view in views:
                hammered_view = deepcopy(view)
                if rng.random() < self.config.get("name_mask_probability", 0.0):
                    hammered_view["presented_schema"] = mask_schema_name(
                        hammered_view["presented_schema"]
                    )
                hammered_view["schema_pool"] = inject_irrelevant_tools(
                    hammered_view["presented_schema"],
                    count=self.config.get("irrelevant_tool_count", 0),
                )
                masked_views.append(hammered_view)
            return masked_views

        return views

    def run(self, *, mode: str | None = None, max_steps: int = 2) -> str:
        effective_mode = mode or self.config["mode"]
        rows = load_dataset_rows(self.config)
        training_views = self._build_views(rows, effective_mode)
        method_name = effective_mode
        run_dir = ensure_run_dir(self.config["run_root"], method_name, self.config.get("seed", 0))

        preview_views = training_views[: max(1, min(max_steps, len(training_views)))]
        predictions = [
            {
                "semantic_task_id": view["semantic_task_id"],
                "variant": view["variant"],
                "status": "smoke_only_no_model",
                "presented_schema": view["presented_schema"],
                "target_call": view["target_call"],
                "predicted_call": None,
            }
            for view in preview_views
        ]

        metrics = build_common_metrics(
            self.config,
            method_name=method_name,
            max_steps=max_steps,
            num_examples=len(training_views),
            extra_metrics={
                "mode": effective_mode,
                "schema_augmentation": effective_mode in {"schema_augmented_sft", "hammer_like"},
                "name_mask_probability": self.config.get("name_mask_probability", 0.0),
                "irrelevant_tool_count": self.config.get("irrelevant_tool_count", 0),
                "num_raw_examples": len(rows),
                "num_training_views": len(training_views),
            },
        )

        write_json(run_dir / "metrics.json", metrics)
        write_predictions(run_dir / "predictions.jsonl", predictions)
        return str(run_dir)
