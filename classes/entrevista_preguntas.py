import json
from datetime import datetime


class EntrevistaPreguntas:
    def __init__(self):
        # Lista de categorías esperadas para validación
        self.expected_categories = ["General", "Semaforo", "Pictogramas", "Tabla", "Comparacion", "Cierre"]
        
        # Diccionario para almacenar preguntas por categoría, cada pregunta es un dict
        self.preguntas = {
            "General": [
                {
                    "texto": "¿Qué tan familiarizadas están ustedes con el uso de celulares o pantallas digitales?",
                    "tipo": "text",
                    "requerida": True
                },
                {
                    "texto": "¿Cuando observan estas interfaces, qué es lo primero que entienden sin que se los explique?",
                    "tipo": "text",
                    "requerida": True
                }
            ],
            "Semaforo": [
                {
                    "texto": "¿Qué creen que significa cada color (verde, amarillo, rojo)?",
                    "tipo": "text",
                    "requerida": True
                },
                {
                    "texto": "¿Les resulta fácil identificar el estado del cultivo con este sistema de colores?",
                    "tipo": "text",
                    "requerida": True
                },
                {
                    "texto": "¿Qué ventajas le ven a esta forma de mostrar la información?",
                    "tipo": "text",
                    "requerida": False
                },
                {
                    "texto": "¿Qué dificultades podrían tener con este diseño?",
                    "tipo": "text",
                    "requerida": False
                },
                {
                    "texto": "¿Si tuvieran que tomar una decisión rápida (regar o no regar), esta interfaz les ayuda?",
                    "tipo": "text",
                    "requerida": False
                }
            ],
            "Pictogramas": [
                {
                    "texto": "¿Qué representa la gota que está medio llena?",
                    "tipo": "text",
                    "requerida": True
                },
                {
                    "texto": "¿Les resulta más fácil entender la humedad viendo una gota medio llena o leyendo un número?",
                    "tipo": "text",
                    "requerida": True
                },
                {
                    "texto": "¿Qué tan claro les parece el sol y la nube para representar el clima?",
                    "tipo": "text",
                    "requerida": True
                },
                {
                    "texto": "¿Qué ventajas encuentran en este diseño?",
                    "tipo": "text",
                    "requerida": False
                },
                {
                    "texto": "¿Qué dificultades podrían surgir al interpretar las imágenes?",
                    "tipo": "text",
                    "requerida": False
                }
            ],
            "Tabla": [
                {
                    "texto": "¿Pueden identificar fácilmente qué significa cada fila de la tabla?",
                    "tipo": "text",
                    "requerida": True
                },
                {
                    "texto": "¿Qué tan claros son los números para tomar decisiones?",
                    "tipo": "text",
                    "requerida": True
                },
                {
                    "texto": "¿Prefieren ver porcentajes exactos o prefieren que se muestre con imágenes (como en la gota)?",
                    "tipo": "text",
                    "requerida": True
                },
                {
                    "texto": "¿Qué ventajas ven en este diseño?",
                    "tipo": "text",
                    "requerida": False
                },
                {
                    "texto": "¿Qué dificultades podrían tener para entenderlo?",
                    "tipo": "text",
                    "requerida": False
                }
            ],
            "Comparacion": [
                {
                    "texto": "¿De las tres interfaces (semaforo, pictogramas, tabla), cuál les parece más fácil de entender?",
                    "tipo": "text",
                    "requerida": True
                },
                {
                    "texto": "¿Cuál les da más confianza para tomar una decisión?",
                    "tipo": "text",
                    "requerida": True
                },
                {
                    "texto": "¿Cuál creen que les serviría más en el día a día en el cultivo?",
                    "tipo": "text",
                    "requerida": True
                },
                {
                    "texto": "¿Cambiarían algo en alguna de ellas para hacerla más clara?",
                    "tipo": "text",
                    "requerida": False
                }
            ],
            "Cierre": [
                {
                    "texto": "¿Hay algo que les gustaría agregar o sugerir para mejorar estas interfaces?",
                    "tipo": "text",
                    "requerida": False
                },
                {
                    "texto": "¿Si tuvieran que recomendar una sola de estas interfaces a otras campesinas, cuál sería y por qué?",
                    "tipo": "text",
                    "requerida": False
                }
            ]
        }
        self.total_preguntas = sum(len(categoria) for categoria in self.preguntas.values())

    def crear_pregunta(self, categoria, pregunta_dict):
        """Añade una nueva pregunta (dict) a la categoría especificada."""
        if categoria in self.preguntas:
            self.preguntas[categoria].append(pregunta_dict)
            self.total_preguntas += 1
            return True
        return False

    def eliminar_pregunta(self, categoria, indice):
        """Elimina una pregunta de la categoría especificada por su índice."""
        if categoria in self.preguntas and 0 <= indice < len(self.preguntas[categoria]):
            del self.preguntas[categoria][indice]
            self.total_preguntas -= 1
            return True
        return False

    def actualizar_pregunta(self, categoria, indice, pregunta_dict):
        """Actualiza una pregunta en la categoría especificada."""
        if categoria in self.preguntas and 0 <= indice < len(self.preguntas[categoria]):
            self.preguntas[categoria][indice] = pregunta_dict
            return True
        return False

    def subir_pregunta(self, categoria, indice):
        """Sube una pregunta en la categoría (intercambia con la anterior)."""
        if categoria in self.preguntas and 0 < indice < len(self.preguntas[categoria]):
            self.preguntas[categoria][indice], self.preguntas[categoria][indice - 1] = \
                self.preguntas[categoria][indice - 1], self.preguntas[categoria][indice]
            return True
        return False

    def bajar_pregunta(self, categoria, indice):
        """Baja una pregunta en la categoría (intercambia con la siguiente)."""
        if categoria in self.preguntas and 0 <= indice < len(self.preguntas[categoria]) - 1:
            self.preguntas[categoria][indice], self.preguntas[categoria][indice + 1] = \
                self.preguntas[categoria][indice + 1], self.preguntas[categoria][indice]
            return True
        return False

    def obtener_preguntas(self, categoria=None):
        """Devuelve todas las preguntas o las de una categoría específica."""
        if categoria and categoria in self.preguntas:
            return self.preguntas[categoria]
        return self.preguntas

    def obtener_pregunta(self, categoria, indice):
        """Devuelve una pregunta específica por categoría e índice."""
        if categoria in self.preguntas and 0 <= indice < len(self.preguntas[categoria]):
            return self.preguntas[categoria][indice]
        return None

    def exportar_json(self, filename="preguntas.json"):
        """Exporta las preguntas a un archivo JSON."""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.preguntas, f, ensure_ascii=False, indent=2)
        return filename

    def importar_json(self, filename="preguntas.json"):
        """Importa preguntas desde un archivo JSON y actualiza el cuestionario."""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                imported_preguntas = json.load(f)
            # Validar estructura básica
            for cat, preguntas in imported_preguntas.items():
                if not isinstance(preguntas, list):
                    return False
                for p in preguntas:
                    if not isinstance(p, dict) or "texto" not in p:
                        return False
            # Validar que las categorías coincidan con las esperadas (para evitar formatos viejos)
            if set(imported_preguntas.keys()) != set(self.expected_categories):
                return False
            self.preguntas = imported_preguntas
            self.total_preguntas = sum(len(categoria) for categoria in self.preguntas.values())
            return True
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return False

    def __str__(self):
        """Representación en cadena para depuración."""
        return "\n".join([
            f"{cat}: " + "; ".join([f"{i+1}. {p['texto']}" for i, p in enumerate(preguntas)])
            for cat, preguntas in self.preguntas.items()
        ])


if __name__ == "__main__":
    # Ejemplo de uso
    entrevista = EntrevistaPreguntas()
    print("Preguntas iniciales:")
    print(entrevista)

    # Exportar a JSON
    entrevista.exportar_json("preguntas.json")

    # Importar desde JSON
    entrevista.importar_json("preguntas.json")
    print("\nDespués de importar desde JSON:")
    print(entrevista)