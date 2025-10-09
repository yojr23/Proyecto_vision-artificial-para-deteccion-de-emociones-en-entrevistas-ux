import json
from pathlib import Path
from datetime import datetime

class ReporteEntrevista:
    def __init__(self, entrevista_id: str):
        self.id = entrevista_id
        self.creado_en = datetime.now().isoformat()
        self.preguntas = []  # lista de dicts con info de cada pregunta
        self.resumen = {}    # se llena al generar_resumen()

    def agregar_pregunta(self, pregunta_id: int, inicio: float, fin: float, nota: str = ""):
        self.preguntas.append({
            "pregunta_id": pregunta_id,
            "inicio": inicio,
            "fin": fin,
            "nota": nota,
            "duracion": fin - inicio if fin and inicio else None
        })

    def generar_resumen(self):
        total_preguntas = len(self.preguntas)
        total_con_nota = sum(1 for p in self.preguntas if p["nota"])
        duracion_total = sum(p["duracion"] for p in self.preguntas if p["duracion"])

        self.resumen = {
            "entrevista_id": self.id,
            "total_preguntas": total_preguntas,
            "preguntas_con_nota": total_con_nota,
            "duracion_total": duracion_total,
            "creado_en": self.creado_en
        }
        return self.resumen

    def exportar_json(self, ruta):  # Eliminar la anotación de tipo temporalmente
        data = {
            "resumen": self.resumen,
            "preguntas": self.preguntas
        }
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return ruta

    def __str__(self):
        return f"ReporteEntrevista({self.id}, {len(self.preguntas)} preguntas)"
