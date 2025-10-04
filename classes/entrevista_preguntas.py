import json
from datetime import datetime


class EntrevistaPreguntas:
    def __init__(self):
        # Diccionario para almacenar preguntas por categoría (más legible que A, B, C...)
        self.preguntas = {
            "General": [
                "¿Qué tan familiarizadas están ustedes con el uso de celulares o pantallas digitales?",
                "¿Cuando observan estas interfaces, qué es lo primero que entienden sin que se los explique?"
            ],
            "Semaforo": [
                "¿Qué creen que significa cada color (verde, amarillo, rojo)?",
                "¿Les resulta fácil identificar el estado del cultivo con este sistema de colores?",
                "¿Qué ventajas le ven a esta forma de mostrar la información?",
                "¿Qué dificultades podrían tener con este diseño?",
                "¿Si tuvieran que tomar una decisión rápida (regar o no regar), esta interfaz les ayuda?"
            ],
            "Pictogramas": [
                "¿Qué representa la gota que está medio llena?",
                "¿Les resulta más fácil entender la humedad viendo una gota medio llena o leyendo un número?",
                "¿Qué tan claro les parece el sol y la nube para representar el clima?",
                "¿Qué ventajas encuentran en este diseño?",
                "¿Qué dificultades podrían surgir al interpretar las imágenes?"
            ],
            "Tabla": [
                "¿Pueden identificar fácilmente qué significa cada fila de la tabla?",
                "¿Qué tan claros son los números para tomar decisiones?",
                "¿Prefieren ver porcentajes exactos o prefieren que se muestre con imágenes (como en la gota)?",
                "¿Qué ventajas ven en este diseño?",
                "¿Qué dificultades podrían tener para entenderlo?"
            ],
            "Comparacion": [
                "¿De las tres interfaces (semaforo, pictogramas, tabla), cuál les parece más fácil de entender?",
                "¿Cuál les da más confianza para tomar una decisión?",
                "¿Cuál creen que les serviría más en el día a día en el cultivo?",
                "¿Cambiarían algo en alguna de ellas para hacerla más clara?"
            ],
            "Cierre": [
                "¿Hay algo que les gustaría agregar o sugerir para mejorar estas interfaces?",
                "¿Si tuvieran que recomendar una sola de estas interfaces a otras campesinas, cuál sería y por qué?"
            ]
        }
        self.total_preguntas = sum(len(categoria) for categoria in self.preguntas.values())

    def crear_pregunta(self, categoria, pregunta):
        """Añade una nueva pregunta a la categoría especificada."""
        if categoria in self.preguntas:
            self.preguntas[categoria].append(pregunta)
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
                self.preguntas = json.load(f)
            self.total_preguntas = sum(len(categoria) for categoria in self.preguntas.values())
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False

    def __str__(self):
        """Representación en cadena para depuración."""
        return "\n".join([
            f"{cat}: " + "; ".join([f"{i+1}. {p}" for i, p in enumerate(preguntas)])
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
