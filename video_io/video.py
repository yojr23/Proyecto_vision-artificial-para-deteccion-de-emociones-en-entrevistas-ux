from abc import ABC, abstractmethod
import platform
import os
import cv2
import pyaudio
import av
from pathlib import Path
import numpy as np

class CapturadorVideo(ABC):
    @abstractmethod
    def iniciar_grabacion(self, ruta_archivo: str, resolucion: str = '720p', codec: str = 'H.264', audio: str = 'AAC'):
        """Inicia la grabación de video y audio en el archivo especificado."""
        pass

    @abstractmethod
    def detener_grabacion(self):
        """Detiene la grabación y cierra el archivo de video."""
        pass

    @abstractmethod
    def procesar_frame(self, frame):
        """Procesa un frame de video para grabarlo."""
        pass


class CapturadorVideoMacOS(CapturadorVideo):
    def __init__(self):
        self.ffmpeg_process = None
        self.output_file = None

    def iniciar_grabacion(self, ruta_archivo: str, resolucion: str = '720p', codec: str = 'h264', audio: str = 'AAC'):
        import subprocess
        if self.ffmpeg_process is not None:
            raise RuntimeError("Grabación ya en curso")

        ruta_path = Path(ruta_archivo)
        if not ruta_path.parent.is_dir():
            raise ValueError(f"El directorio {ruta_path.parent} no existe")

        resolucion_map = {'720p': '1280x720'}
        if resolucion not in resolucion_map:
            raise ValueError(f"Resolución {resolucion} no soportada")
        video_size = resolucion_map[resolucion]

        # avfoundation: video_index:audio_index, normalmente 0:0 para cámara/micrófono por defecto
        # Puedes cambiar los índices si tienes más de un dispositivo
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'avfoundation',
            '-framerate', '30',
            '-video_size', video_size,
            '-i', '0:1',
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-c:a', 'aac',
            '-pix_fmt', 'yuv420p',
            '-vsync', '2',
            '-async', '1',
            '-y',  # overwrite
            ruta_archivo
        ]
        try:
            self.ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.output_file = ruta_archivo
            print(f"Iniciando grabación con ffmpeg en {ruta_archivo} (cámara y micrófono por defecto)")
        except Exception as e:
            self.ffmpeg_process = None
            raise RuntimeError(f"Error al iniciar ffmpeg: {str(e)}")

    def procesar_frame(self, frame):
        # No es necesario con ffmpeg, pero se mantiene para compatibilidad con la UI
        pass

    def detener_grabacion(self):
        import signal
        if self.ffmpeg_process is None:
            raise RuntimeError("No hay grabación en curso")
        try:
            self.ffmpeg_process.send_signal(signal.SIGINT)
            self.ffmpeg_process.wait(timeout=5)
            print(f"Grabación detenida y guardada en {self.output_file}")
        except Exception as e:
            self.ffmpeg_process.kill()
            print(f"ffmpeg forzado a terminar: {e}")
        finally:
            self.ffmpeg_process = None
            self.output_file = None
            

class CapturadorVideoWindows(CapturadorVideo):
    def __init__(self):
        self.cap = None
        self.out = None
        self.audio = None
        self.stream = None
        self.is_recording = False

    def iniciar_grabacion(self, ruta_archivo: str, resolucion: str = '720p', codec: str = 'H.264', audio: str = 'AAC'):
        if self.is_recording:
            raise RuntimeError("Grabación ya en curso")

        ruta_path = Path(ruta_archivo)
        if not ruta_path.parent.is_dir():
            raise ValueError(f"El directorio {ruta_path.parent} no existe")

        resolucion_map = {'720p': (1280, 720)}
        if resolucion not in resolucion_map:
            raise ValueError(f"Resolución {resolucion} no soportada")
        width, height = resolucion_map[resolucion]

        fourcc_map = {'H.264': cv2.VideoWriter_fourcc(*'X264')}
        if codec not in fourcc_map:
            raise ValueError(f"Codec {codec} no soportado")
        fourcc = fourcc_map[codec]

        try:
            self.out = cv2.VideoWriter(ruta_archivo, fourcc, 30.0, (width, height))

            if audio == 'AAC':
                self.audio = pyaudio.PyAudio()
                self.stream = self.audio.open(format=pyaudio.paInt16,
                                              channels=1,
                                              rate=44100,
                                              input=True,
                                              frames_per_buffer=1024)

            self.is_recording = True
            print(f"Iniciando grabación en {ruta_archivo} con {resolucion}, {codec}, {audio} en Windows")
        except Exception as e:
            self.detener_grabacion()
            raise RuntimeError(f"Error al iniciar grabación en Windows: {str(e)}")

    def procesar_frame(self, frame):
        if self.is_recording and self.out:
            self.out.write(frame)

    def detener_grabacion(self):
        if not self.is_recording:
            raise RuntimeError("No hay grabación en curso")
        try:
            if self.out:
                self.out.release()
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.audio:
                self.audio.terminate()
            print("Deteniendo grabación en Windows")
        finally:
            self.out = None
            self.audio = None
            self.stream = None
            self.is_recording = False


def obtener_capturador():
    sistema = platform.system()
    if sistema == 'Darwin':
        return CapturadorVideoMacOS()
    elif sistema == 'Windows':
        return CapturadorVideoWindows()
    else:
        raise NotImplementedError(f"Sistema operativo {sistema} no soportado")