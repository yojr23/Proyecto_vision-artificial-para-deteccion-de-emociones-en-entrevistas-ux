import json
from pathlib import Path
from typing import List, Optional
from classes.marca import Marca

class Marcas:
    def __init__(self, entrevista_id: str, archivo_video: Path):
        self.entrevista_id = entrevista_id
        self.archivo_video = archivo_video
        self.marcas: List[Marca] = []

    def agregar_marca(self, marca: Marca):
        """Añade una marca, validando que no se solape y que pertenezca a la entrevista."""
        if not isinstance(marca, Marca):
            raise TypeError("El parámetro 'marca' debe ser una instancia de Marca")
        if marca.entrevista_id != self.entrevista_id:
            raise ValueError(f"La marca tiene entrevista_id {marca.entrevista_id}, pero se esperaba {self.entrevista_id}")
        if self._existe_solapamiento(marca):
            raise ValueError(f"La marca con pregunta_id {marca.pregunta_id} se solapa con otra existente")
        self.marcas.append(marca)
        self._guardar_marcas_json()

    def eliminar_marca(self, pregunta_id: int):
        """Elimina una marca por su pregunta_id."""
        self.marcas = [m for m in self.marcas if m.pregunta_id != pregunta_id]
        self._guardar_marcas_json()

    def buscar_marcas_por_pregunta_id(self, pregunta_id: int) -> Optional[Marca]:
        """Busca una marca por su pregunta_id."""
        for marca in self.marcas:
            if marca.pregunta_id == pregunta_id:
                return marca
        return None

    def exportar_json(self, ruta_json: Path):
        """Exporta las marcas a un archivo JSON."""
        data = {
            "entrevista_id": self.entrevista_id,
            "archivo_video": str(self.archivo_video),
            "marcas": [
                {
                    "entrevista_id": marca.entrevista_id,
                    "pregunta_id": marca.pregunta_id,
                    "inicio": marca.inicio,
                    "fin": marca.fin,
                    "nota": marca.nota
                } for marca in self.marcas
            ]
        }
        ruta_json.parent.mkdir(parents=True, exist_ok=True)
        with open(ruta_json, 'w') as f:
            json.dump(data, f, indent=2)
            f.flush()

    def importar_json(self, ruta_json: Path):
        """Importa marcas desde un archivo JSON."""
        if not ruta_json.exists():
            raise FileNotFoundError(f"El archivo {ruta_json} no existe")
        with open(ruta_json, 'r') as f:
            data = json.load(f)
        if data["entrevista_id"] != self.entrevista_id:
            raise ValueError("El entrevista_id del JSON no coincide")
        self.archivo_video = Path(data["archivo_video"])
        self.marcas = [
            Marca(
                entrevista_id=m["entrevista_id"],
                pregunta_id=m["pregunta_id"],
                inicio=m["inicio"],
                fin=m.get("fin"),
                nota=m.get("nota", "")
            ) for m in data["marcas"]
        ]

    def _existe_solapamiento(self, nueva_marca: Marca) -> bool:
        """Valida si una nueva marca se solapa con las existentes."""
        if nueva_marca.fin is None:
            return False  # No se puede validar solapamiento sin fin
        for marca in self.marcas:
            if marca.fin is None:
                continue
            if nueva_marca.inicio < marca.fin and nueva_marca.fin > marca.inicio:
                return True
        return False

    def _guardar_marcas_json(self):
        """Guarda las marcas en el archivo JSON especificado."""
        self.exportar_json(Path(f"data/marcas/marcas_{self.entrevista_id}.json"))