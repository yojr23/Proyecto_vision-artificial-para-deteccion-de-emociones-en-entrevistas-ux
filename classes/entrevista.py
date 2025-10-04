import os
import json
from datetime import datetime
from pathlib import Path
from classes.marcas import Marcas
from classes.marca import Marca
from classes.fragmento import Fragmento 
from classes.reporte_entrevista import ReporteEntrevista as Reporte
from video_io.video import obtener_capturador, CapturadorVideo

class Entrevista:
    def __init__(self, salida_dir="data", entrevista_num=1, entrevista_id=None):
        if entrevista_id:
            self.id = entrevista_id
        else:
            self.id = f"{datetime.now().strftime('%Y-%m-%d')}_{entrevista_num:03d}"
            
        self.inicio_wall = datetime.now().isoformat()
        self.esta_grabando = False
        self.tiempo_inicio = None
        self.capturador = obtener_capturador()

        # Rutas
        salida_path = Path(salida_dir)
        if not salida_path.is_dir():
            raise ValueError(f"El directorio {salida_dir} no existe o no es válido")
        
        self.video_original = salida_path / "videos_originales" / f"entrevista_{self.id}.mp4"
        self.fragmentos_dir = salida_path / "fragmentos"
        self.marcas_json = salida_path / "marcas" / f"marcas_{self.id}.json"

        # Crear carpetas
        self.video_original.parent.mkdir(parents=True, exist_ok=True)
        self.fragmentos_dir.mkdir(parents=True, exist_ok=True)
        self.marcas_json.parent.mkdir(parents=True, exist_ok=True)

        # Atributos POO
        self.marcas = Marcas(self.id, self.video_original)  # Instancia de Marcas
        self.fragmentos = []  # Lista de objetos Fragmento
        self.reporte = Reporte(self.id)
        self.pregunta_actual_id = 0

        # Crear JSON inicial
        self.marcas.exportar_json(self.marcas_json)

    def iniciar(self):
        """Inicia la grabación de la entrevista y registra el tiempo de inicio."""
        if self.esta_grabando:
            raise RuntimeError("La entrevista ya está en curso")
        self.tiempo_inicio = datetime.now()
        self.esta_grabando = True
        try:
            self.capturador.iniciar_grabacion(
                ruta_archivo=str(self.video_original),
                resolucion='720p',
                codec='H.264',
                audio='AAC'
            )
        except Exception as e:
            self.esta_grabando = False
            raise RuntimeError(f"Error al iniciar grabación: {str(e)}")
        self.marcas.exportar_json(self.marcas_json)

    def finalizar(self):
        if not self.esta_grabando:
            raise RuntimeError("No hay una entrevista en curso")
        try:
            self.capturador.detener_grabacion()
            for marca in self.marcas.marcas:
                if marca.fin is not None:
                    fragmento = Fragmento(marca, self.fragmentos_dir)
                    fragmento.generar_fragmento(self.video_original)
                    self.agregar_fragmento(fragmento)
                    # Agregar datos al reporte
                    self.reporte.agregar_pregunta(marca.pregunta_id, marca.inicio, marca.fin, marca.nota)
        finally:
            self.esta_grabando = False
            self.marcas.exportar_json(self.marcas_json)
        resumen = self.reporte.generar_resumen()
        self.reporte.exportar_json(self.marcas_json.with_name(f"reporte_{self.id}.json"))
        return resumen


    def marcar_inicio_pregunta(self):
        """Registra el inicio de una pregunta, crea una Marca asociada y devuelve su ID."""
        if not self.esta_grabando:
            raise RuntimeError("La entrevista no está en curso")
        self.pregunta_actual_id += 1
        tiempo_actual = (datetime.now() - self.tiempo_inicio).total_seconds()
        marca = Marca(entrevista_id=self.id, pregunta_id=self.pregunta_actual_id, inicio=tiempo_actual)
        self.marcas.agregar_marca(marca)
        return self.pregunta_actual_id

    def marcar_fin_pregunta(self, pregunta_id: int, nota: str = ""):
        """Registra el fin de una pregunta, asocia la nota y actualiza la Marca."""
        if not self.esta_grabando:
            raise RuntimeError("La entrevista no está en curso")
        marca = self.marcas.buscar_marcas_por_pregunta_id(pregunta_id)
        if marca is None:
            raise ValueError(f"No se encontró una marca con pregunta_id {pregunta_id}")
        if marca.fin is not None:
            raise ValueError(f"La marca con pregunta_id {pregunta_id} ya está cerrada")
        marca.fin = (datetime.now() - self.tiempo_inicio).total_seconds()
        marca.nota = nota
        self.marcas.exportar_json(self.marcas_json)

    def agregar_fragmento(self, fragmento: Fragmento):
        """Añade un fragmento a la entrevista."""
        if not isinstance(fragmento, Fragmento):
            raise TypeError("El parámetro 'fragmento' debe ser una instancia de Fragmento")
        if fragmento.entrevista_id != self.id:
            fragmento.entrevista_id = self.id
        self.fragmentos.append(fragmento)

    def asignar_reporte(self, reporte: Reporte):
        """Asocia un reporte a la entrevista."""
        if not isinstance(reporte, Reporte):
            raise TypeError("El parámetro 'reporte' debe ser una instancia de Reporte")
        if reporte.id != self.id:
            raise ValueError("El ID del reporte debe coincidir con el ID de la entrevista")
        self.reporte = reporte

    def generar_resumen(self):
        """Genera un resumen de la entrevista para mostrar al finalizar."""
        duracion = 0.0
        if self.tiempo_inicio and not self.esta_grabando:
            duracion = (datetime.now() - self.tiempo_inicio).total_seconds()
        return {
            "duracion_segundos": duracion,
            "numero_preguntas": len([m for m in self.marcas.marcas if m.fin is not None]),
            "video_original": str(self.video_original),
            "marcas_json": str(self.marcas_json),
            "entrevista_id": self.id
        }