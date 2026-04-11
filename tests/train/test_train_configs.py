from schema_reuse.train.direct import load_train_config


def test_direct_config_exposes_baseline_mode() -> None:
    config = load_train_config("configs/pilot_v1/train/direct.yaml")
    assert config["mode"] in {"vanilla_sft", "schema_augmented_sft"}


def test_hammer_like_config_enables_name_masking() -> None:
    config = load_train_config("configs/pilot_v1/train/hammer_like.yaml")
    assert config["name_mask_probability"] > 0
