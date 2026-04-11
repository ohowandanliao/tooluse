from __future__ import annotations

from collections import defaultdict
from typing import Iterable


def mean(values: Iterable[int | float | bool]) -> float:
    items = [float(value) for value in values]
    if not items:
        return 0.0
    return sum(items) / len(items)


def accuracy(values: Iterable[int | float | bool]) -> float:
    return mean(values)


def grouped_accuracy(
    values: list[int | float | bool],
    groups: list[str],
) -> dict[str, float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for value, group in zip(values, groups):
        grouped[group].append(float(value))
    return {group: mean(group_values) for group, group_values in grouped.items()}
