from __future__ import annotations

from dataclasses import asdict, dataclass

from schema_reuse.models.bottleneck import BottleneckConfig


@dataclass(frozen=True)
class ReuseModelConfig:
    bottleneck: BottleneckConfig
    cross_schema_weight: float = 1.0
    method_name: str = "reuse_main"

    def __post_init__(self) -> None:
        if not self.bottleneck.enable_reuse:
            raise ValueError("ReuseModelConfig requires enable_reuse=True")
        if self.cross_schema_weight <= 0:
            raise ValueError("cross_schema_weight must be positive")

    def to_dict(self) -> dict[str, object]:
        return {
            "method_name": self.method_name,
            "cross_schema_weight": self.cross_schema_weight,
            "bottleneck": asdict(self.bottleneck),
        }
