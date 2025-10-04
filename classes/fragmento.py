import subprocess
from pathlib import Path
from typing import Optional
from classes.marca import Marca

class Fragmento:
    def __init__(self, marca: Marca, fragmentos_dir: Path):
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
        """Corta un fragmento del video original usando FFmpeg."""
        if not video_original.exists():
            raise FileNotFoundError(f"Video original no encontrado: {video_original}")
        if self.generado:
            raise RuntimeError(f"El fragmento {self.ruta_fragmento} ya fue generado")
        if self.marca.inicio >= self.marca.fin:
            raise ValueError("El tiempo de inicio debe ser menor que el tiempo de fin")

        self.ruta_fragmento.parent.mkdir(parents=True, exist_ok=True)
        
        comando = [
            'ffmpeg',
            '-i', str(video_original),
            '-ss', str(self.marca.inicio),  # Inicio del segmento
            '-t', str(self.duracion),       # Duración del segmento
            '-c:v', 'copy',                # Copia sin re-encode para mayor velocidad
            '-c:a', 'copy',                # Copia audio sin re-encode
            str(self.ruta_fragmento)
        ]
        try:
            subprocess.run(comando, check=True, capture_output=True)
            self.generado = True
            print(f"Fragmento generado: {self.ruta_fragmento}")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error al generar fragmento: {e.stderr.decode()}")