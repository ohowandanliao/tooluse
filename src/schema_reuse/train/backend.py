from __future__ import annotations

import importlib
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class BackendReport:
    torch_available: bool
    transformers_available: bool
    peft_available: bool
    accelerate_available: bool
    torch_version: str | None = None
    transformers_version: str | None = None
    peft_version: str | None = None
    accelerate_version: str | None = None
    ready_for_real_training: bool = False
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _safe_import(name: str) -> tuple[bool, str | None, str | None]:
    try:
        module = importlib.import_module(name)
        return True, getattr(module, "__version__", None), None
    except Exception as exc:  # pragma: no cover - exercised indirectly
        return False, None, f"{type(exc).__name__}: {exc}"


def probe_training_backend() -> BackendReport:
    torch_ok, torch_version, torch_error = _safe_import("torch")
    transformers_ok, transformers_version, transformers_error = _safe_import("transformers")
    peft_ok, peft_version, peft_error = _safe_import("peft")
    accelerate_ok, accelerate_version, accelerate_error = _safe_import("accelerate")

    notes: list[str] = []
    if torch_error:
        notes.append(f"torch: {torch_error}")
    if transformers_error:
        notes.append(f"transformers: {transformers_error}")
    if peft_error:
        notes.append(f"peft: {peft_error}")
    if accelerate_error:
        notes.append(f"accelerate: {accelerate_error}")

    ready = torch_ok and transformers_ok and peft_ok and accelerate_ok

    if ready and torch_version is not None:
        major_minor = tuple(int(part) for part in torch_version.split(".")[:2])
        if major_minor < (2, 4):
            ready = False
            notes.append(
                f"torch version {torch_version} is below the recommended minimum 2.4 for the server training stack"
            )

    return BackendReport(
        torch_available=torch_ok,
        transformers_available=transformers_ok,
        peft_available=peft_ok,
        accelerate_available=accelerate_ok,
        torch_version=torch_version,
        transformers_version=transformers_version,
        peft_version=peft_version,
        accelerate_version=accelerate_version,
        ready_for_real_training=ready,
        notes=tuple(notes),
    )
