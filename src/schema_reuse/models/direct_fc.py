from __future__ import annotations

from dataclasses import dataclass


VALID_DIRECT_MODES = {"vanilla_sft", "schema_augmented_sft", "hammer_like"}


@dataclass(frozen=True)
class DirectFCConfig:
    mode: str
    backbone_model_id: str
    name_mask_probability: float = 0.0
    irrelevant_tool_count: int = 0

    def __post_init__(self) -> None:
        if self.mode not in VALID_DIRECT_MODES:
            raise ValueError(f"Unsupported direct baseline mode: {self.mode}")
        if not 0.0 <= self.name_mask_probability <= 1.0:
            raise ValueError("name_mask_probability must be in [0, 1]")
        if self.irrelevant_tool_count < 0:
            raise ValueError("irrelevant_tool_count must be non-negative")

    @property
    def uses_schema_augmentation(self) -> bool:
        return self.mode in {"schema_augmented_sft", "hammer_like"}
