from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Marca:
    entrevista_id: str  # ID de la entrevista a la que pertenece la marca
    pregunta_id: int
    inicio: float  # Timestamp relativo en segundos
    fin: Optional[float] = None  # None si no ha finalizado
    nota: str = ""  # Nota opcional

    def __post_init__(self):
        if not isinstance(self.entrevista_id, str) or not self.entrevista_id:
            raise ValueError("entrevista_id debe ser un string no vacío")
        if self.pregunta_id <= 0:
            raise ValueError("pregunta_id debe ser un entero positivo")
        if self.inicio < 0:
            raise ValueError("El tiempo de inicio no puede ser negativo")
        if self.fin is not None and self.fin <= self.inicio:
            raise ValueError("El tiempo de fin debe ser mayor que el inicio")

    @property
    def duracion(self) -> Optional[float]:
        """Calcula la duración de la marca si ha finalizado."""
        if self.fin is None:
            return None
        return self.fin - self.inicio