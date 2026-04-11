from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class BottleneckConfig:
    latent_dim: int
    enable_reuse: bool = False
    consistency_weight: float = 0.0

    def __post_init__(self) -> None:
        if self.latent_dim <= 0:
            raise ValueError("latent_dim must be positive")
        if self.latent_dim > 128:
            raise ValueError("latent_dim must be <= 128 for pilot-v1")
        if self.consistency_weight < 0:
            raise ValueError("consistency_weight must be non-negative")

    def to_dict(self) -> dict[str, int | float | bool]:
        return asdict(self)
