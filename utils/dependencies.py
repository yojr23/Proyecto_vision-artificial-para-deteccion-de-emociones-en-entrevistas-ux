"""
Utilities to validate that heavy ML dependencies required by the análisis
module are present before we attempt to load any TensorFlow models.
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class MissingDependency:
    module: str
    pip_hint: str
    reason: str


class DependencyError(RuntimeError):
    """Raised when critical ML dependencies are not available."""


def _missing_modules(requirements: Iterable[MissingDependency]) -> List[MissingDependency]:
    missing = []
    for req in requirements:
        if importlib.util.find_spec(req.module) is None:
            missing.append(req)
    return missing


def ensure_analysis_dependencies() -> None:
    """
    Validate Python version and existence of the heavy ML dependencies required
    by the análisis module. Raises DependencyError with actionable guidance
    when something is missing so the UI can show a friendly message instead of
    crashing in a worker thread.
    """
    # TensorFlow 2.10 (and Mediapipe wheels) run on CPython <= 3.10.
    if sys.version_info < (3, 8) or sys.version_info >= (3, 11):
        raise DependencyError(
            "Python >= 3.8 and < 3.11 is required for TensorFlow/Mediapipe. "
            "Reinstala el entorno usando `pyenv local 3.8.10` como indica el README."
        )

    requirements = [
        MissingDependency(
            module="tensorflow",
            pip_hint="pip install 'tensorflow>=2.10,<2.12'",
            reason="necesario para cargar el modelo de emociones",
        ),
        MissingDependency(
            module="h5py",
            pip_hint="pip install 'h5py>=3.8,<4.0'",
            reason="necesario para leer archivos .h5 del modelo",
        ),
        MissingDependency(
            module="mediapipe",
            pip_hint="pip install 'mediapipe>=0.10,<0.11'",
            reason="necesario para la detección de rostros",
        ),
    ]

    missing = _missing_modules(requirements)
    if missing:
        bullet_list = "\n".join(
            f"  • `{item.module}` ({item.reason}) → {item.pip_hint}" for item in missing
        )
        raise DependencyError(
            "Faltan dependencias críticas para el módulo de análisis.\n"
            "Instala lo siguiente en el mismo entorno virtual antes de continuar:\n"
            f"{bullet_list}"
        )
