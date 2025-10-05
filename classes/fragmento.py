import subprocess
import logging
from pathlib import Path
from typing import Optional
from classes.marca import Marca


class Fragmento:
    def __init__(self, marca: Marca, fragmentos_dir: Path):
        """Representa un fragmento de video basado en una marca de tiempo."""
        self.logger = logging.getLogger(__name__)

        if not isinstance(marca, Marca):
            raise TypeError("El parámetro 'marca' debe ser una instancia de Marca")
        if marca.fin is None:
            raise ValueError("La marca debe estar finalizada para crear un fragmento")

        self.marca = marca
        self.entrevista_id = marca.entrevista_id  # Heredado de la marca
        self.ruta_fragmento = fragmentos_dir / f"fragmento_{marca.entrevista_id}_{marca.pregunta_id:03d}.mp4"
        self.duracion = self.marca.fin - self.marca.inicio
        self.generado = False

    def generar_fragmento(self, video_original: Path):
        """Corta un fragmento del video original usando FFmpeg con precisión de fotogramas."""
        if not video_original.exists():
            raise FileNotFoundError(f"Video original no encontrado: {video_original}")
        if self.generado:
            raise RuntimeError(f"El fragmento {self.ruta_fragmento} ya fue generado")
        if self.marca.inicio >= self.marca.fin:
            raise ValueError("El tiempo de inicio debe ser menor que el tiempo de fin")

        self.ruta_fragmento.parent.mkdir(parents=True, exist_ok=True)

        comando = [
            'ffmpeg',
            '-ss', str(self.marca.inicio),   # búsqueda antes de -i (más preciso)
            '-i', str(video_original),
            '-t', str(self.duracion),
            '-c:v', 'libx264',              # reencodear video para evitar frames negros
            '-preset', 'ultrafast',         # reencode rápido
            '-c:a', 'aac',                  # reencode audio
            '-b:a', '128k',
            '-movflags', '+faststart',
            '-y',                           # sobrescribir si existe
            str(self.ruta_fragmento)
        ]

        try:
            self.logger.info(f"Iniciando generación de fragmento: {self.ruta_fragmento.name}")
            result = subprocess.run(
                comando, check=True, capture_output=True, text=True
            )
            self.generado = True
            self.logger.info(f"✅ Fragmento generado correctamente: {self.ruta_fragmento}")
        except subprocess.CalledProcessError as e:
            error_output = e.stderr or e.stdout
            self.logger.error(f"❌ Error al generar fragmento ({self.ruta_fragmento.name}): {error_output}")
            raise RuntimeError(f"Error al generar fragmento: {error_output}")
