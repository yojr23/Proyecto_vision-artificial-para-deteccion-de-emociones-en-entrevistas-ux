from abc import ABC, abstractmethod
import platform
from pathlib import Path
import cv2

# Algunas dependencias opcionales (importar bajo demanda)
# pyaudio y av se importan solo en plataformas que las usan

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
        # Si el sistema requiere distintos índices, el usuario debe ajustarlos.
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
        # No es necesario con ffmpeg (se captura directamente desde dispositivo),
        # pero se mantiene para compatibilidad con la UI.
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
        self.out = None
        self.audio = None
        self.stream = None
        self.is_recording = False

    def iniciar_grabacion(self, ruta_archivo: str, resolucion: str = '720p', codec: str = 'H.264', audio: str = 'AAC'):
        # Importar pyaudio localmente para que la importación del módulo no falle en otros SO
        import pyaudio
        if self.is_recording:
            raise RuntimeError("Grabación ya en curso")

        ruta_path = Path(ruta_archivo)
        if not ruta_path.parent.is_dir():
            raise ValueError(f"El directorio {ruta_path.parent} no existe")

        resolucion_map = {'720p': (1280, 720)}
        if resolucion not in resolucion_map:
            raise ValueError(f"Resolución {resolucion} no soportada")
        width, height = resolucion_map[resolucion]

        # Mapeo simple de fourcc (puede variar según sistema/instalación de OpenCV)
        fourcc_map = {'H.264': cv2.VideoWriter_fourcc(*'X264'), 'MJPG': cv2.VideoWriter_fourcc(*'MJPG')}
        if codec not in fourcc_map:
            raise ValueError(f"Codec {codec} no soportado")
        fourcc = fourcc_map[codec]

        try:
            # Crear writer de video
            self.out = cv2.VideoWriter(str(ruta_archivo), fourcc, 30.0, (width, height))

            # Iniciar captura de audio si se solicita
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
            # Si ocurre error, limpiar recursos parciales
            try:
                if self.out:
                    self.out.release()
            except Exception:
                pass
            try:
                if self.stream:
                    self.stream.stop_stream()
                    self.stream.close()
            except Exception:
                pass
            try:
                if self.audio:
                    self.audio.terminate()
            except Exception:
                pass
            self.out = None
            self.stream = None
            self.audio = None
            self.is_recording = False
            raise RuntimeError(f"Error al iniciar grabación en Windows: {str(e)}")

    def procesar_frame(self, frame):
        # Espera recibir frames en BGR (OpenCV). Debe coincidir con la fuente de video.
        if self.is_recording and self.out:
            try:
                self.out.write(frame)
            except Exception as e:
                print(f"Error escribiendo frame: {e}")

    def detener_grabacion(self):
        if not self.is_recording:
            raise RuntimeError("No hay grabación en curso")
        try:
            if self.out:
                self.out.release()
            if self.stream:
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                except Exception:
                    pass
            if self.audio:
                try:
                    self.audio.terminate()
                except Exception:
                    pass
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
        # Para otros sistemas (Linux) devolvemos un capturador básico que usa OpenCV
        class CapturadorVideoLinux(CapturadorVideo):
            def __init__(self):
                self.out = None
                self.is_recording = False

            def iniciar_grabacion(self, ruta_archivo: str, resolucion: str = '720p', codec: str = 'H.264', audio: str = 'AAC'):
                resolucion_map = {'720p': (1280, 720)}
                if resolucion not in resolucion_map:
                    raise ValueError(f"Resolución {resolucion} no soportada")
                width, height = resolucion_map[resolucion]
                fourcc = cv2.VideoWriter_fourcc(*'X264')
                self.out = cv2.VideoWriter(str(ruta_archivo), fourcc, 30.0, (width, height))
                self.is_recording = True
                print(f"Iniciando grabación en {ruta_archivo} en Linux (sin audio)")

            def procesar_frame(self, frame):
                if self.is_recording and self.out:
                    self.out.write(frame)

            def detener_grabacion(self):
                if self.out:
                    self.out.release()
                self.out = None
                self.is_recording = False
                print("Grabación detenida en Linux (sin audio)")

        return CapturadorVideoLinux()