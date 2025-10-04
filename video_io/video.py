from abc import ABC, abstractmethod
import platform
import os
import cv2
import pyaudio
import av
from pathlib import Path


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
        self.container = None
        self.video_stream = None
        self.audio_stream = None
        self.device = None

    def iniciar_grabacion(self, ruta_archivo: str, resolucion: str = '720p', codec: str = 'h264', audio: str = 'AAC'):
        if self.container:
            raise RuntimeError("Grabación ya en curso")

        ruta_path = Path(ruta_archivo)
        if not ruta_path.parent.is_dir():
            raise ValueError(f"El directorio {ruta_path.parent} no existe")

        resolucion_map = {'720p': (1280, 720)}
        if resolucion not in resolucion_map:
            raise ValueError(f"Resolución {resolucion} no soportada")
        width, height = resolucion_map[resolucion]

        try:
            self.container = av.open(ruta_archivo, mode='w')
            self.video_stream = self.container.add_stream(codec, rate=30)
            self.video_stream.width = width
            self.video_stream.height = height
            self.video_stream.pix_fmt = 'yuv420p'

            if audio == 'AAC':
                self.audio_stream = self.container.add_stream('aac')
                self.audio_stream.bit_rate = 128000

            print(f"Iniciando grabación en {ruta_archivo} con {resolucion}, {codec}, {audio} en macOS")
        except Exception as e:
            self.detener_grabacion()
            raise RuntimeError(f"Error al iniciar grabación en macOS: {str(e)}")

    def procesar_frame(self, frame):
        if not self.container or not self.video_stream:
            return
        frame_av = av.VideoFrame.from_ndarray(frame, format='bgr24')
        packet = self.video_stream.encode(frame_av)
        if packet:
            self.container.mux(packet)

    def detener_grabacion(self):
        if not self.container:
            raise RuntimeError("No hay grabación en curso")
        try:
            if self.video_stream:
                self.video_stream.encode(None)  # Flush encoder
            self.container.close()
            print("Deteniendo grabación en macOS")
        finally:
            self.container = None
            self.video_stream = None
            self.audio_stream = None
            self.device = None


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