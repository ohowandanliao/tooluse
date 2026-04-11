from schema_reuse.models.bottleneck import BottleneckConfig


def test_bottleneck_config_is_capacity_bounded() -> None:
    config = BottleneckConfig(latent_dim=64)
    assert config.latent_dim <= 128


def test_reuse_config_enables_cross_schema_objective() -> None:
    config = BottleneckConfig(latent_dim=64, enable_reuse=True)
    assert config.enable_reuse is True
