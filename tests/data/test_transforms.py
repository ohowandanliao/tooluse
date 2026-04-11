from schema_reuse.data.transforms import apply_transform, build_transform


def test_transform_is_bijective_for_names() -> None:
    schema = {"name": "weather_lookup", "parameters": ["city", "day"]}
    transform = build_transform(schema, seed=7)
    mapped = apply_transform(schema, transform)
    assert mapped["name"] != "weather_lookup"
    assert len(set(transform["arg_map"].values())) == len(transform["arg_map"])


def test_test_vocab_is_disjoint_from_train_vocab() -> None:
    transform = build_transform({"name": "x", "parameters": ["a"]}, seed=1, split="test")
    assert transform["tool_map"]["x"].startswith("test_")
