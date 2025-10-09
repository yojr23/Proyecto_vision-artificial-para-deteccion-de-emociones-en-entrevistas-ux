import logging
import os
import json
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QFrame,
    QTextEdit, QSplitter, QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor
import cv2
import traceback

# Importar clases del proyecto
from classes.marcas import Marcas
from classes.fragmento import Fragmento


class GenerationThread(QThread):
    """Hilo de fondo para generar analisis sin congelar la UI"""
    progress_updated = Signal(int)
    log_message = Signal(str)
    finished_with_success = Signal(int, int)
    error_occurred = Signal(str)

    def __init__(self, video_path, marcas_obj, fragmentos_dir):
        super().__init__()
        self.video_path = video_path
        self.marcas_obj = marcas_obj
        self.fragmentos_dir = fragmentos_dir
        self.logger = logging.getLogger(__name__)

    def run(self):
        try:
            marcas = self.marcas_obj.marcas
            total = len(marcas)
            exitos = 0

            if total == 0:
                self.log_message.emit("⚠️ No hay marcas válidas para procesar.")
                self.finished_with_success.emit(0, 0)
                return

            for idx, marca in enumerate(marcas, 1):
                try:
                    # Validación de tiempos
                    if marca.fin is None or marca.fin <= marca.inicio:
                        msg = f"⚠️ Marca inválida (pregunta {marca.pregunta_id}): tiempos incorrectos."
                        self.log_message.emit(msg)
                        self.logger.warning(msg)
                        continue

                    # Generación del fragmento
                    fragmento = Fragmento(marca, self.fragmentos_dir)
                    fragmento.generar_fragmento(self.video_path)
                    msg = f"✅ Fragmento analizado correctamente: {fragmento.ruta_fragmento.name}"
                    self.log_message.emit(msg)
                    self.logger.info(msg)
                    exitos += 1

                except Exception as e:
                    error_msg = f"❌ Error al analizar fragmento (pregunta {getattr(marca, 'pregunta_id', '?')}): {e}"
                    self.log_message.emit(error_msg)
                    self.logger.error(error_msg)
                    self.logger.debug(traceback.format_exc())

                # Emitir progreso
                self.progress_updated.emit(int((idx / total) * 100))

            self.progress_updated.emit(100)
            self.finished_with_success.emit(exitos, total)
            self.log_message.emit(f"🏁 Proceso finalizado ({exitos}/{total})")

        except Exception as e:
            error_msg = f"🔥 Error crítico en hilo de analisis: {e}"
            self.logger.critical(error_msg)
            self.logger.debug(traceback.format_exc())
            self.error_occurred.emit(error_msg)

class AnalisisGenerarScreen(QWidget):
    """Pantalla para generar fragmentos desde marcas de video"""
    def __init__(self, logger=None, data_context=None, parent=None):
        super().__init__(parent)
        self.logger = logger or logging.getLogger(__name__)
        self.parent_window = parent
        self.videos_data = []
        self.data_context = data_context or {"videos": [], "marcas": {}, "fragmentos": []}
        self.marcas_obj = None
        self.setup_ui()