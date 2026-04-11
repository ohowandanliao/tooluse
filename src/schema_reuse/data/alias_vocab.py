from __future__ import annotations

import random


def build_alias_map(
    names: list[str],
    *,
    seed: int,
    split: str,
    namespace: str,
) -> dict[str, str]:
    unique_names = list(dict.fromkeys(names))
    rng = random.Random(f"{split}:{namespace}:{seed}:{'|'.join(unique_names)}")
    shuffled_indices = list(range(len(unique_names)))
    rng.shuffle(shuffled_indices)

    alias_map: dict[str, str] = {}
    for index, name in enumerate(unique_names):
        alias_map[name] = f"{split}_{namespace}_{shuffled_indices[index]:04d}"
    return alias_map
