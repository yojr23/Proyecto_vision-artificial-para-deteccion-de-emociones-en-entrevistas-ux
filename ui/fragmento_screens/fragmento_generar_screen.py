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
    """Hilo de fondo para generar fragmentos sin congelar la UI"""
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
                    msg = f"✅ Fragmento generado correctamente: {fragmento.ruta_fragmento.name}"
                    self.log_message.emit(msg)
                    self.logger.info(msg)
                    exitos += 1

                except Exception as e:
                    error_msg = f"❌ Error al generar fragmento (pregunta {getattr(marca, 'pregunta_id', '?')}): {e}"
                    self.log_message.emit(error_msg)
                    self.logger.error(error_msg)
                    self.logger.debug(traceback.format_exc())

                # Emitir progreso
                self.progress_updated.emit(int((idx / total) * 100))

            self.progress_updated.emit(100)
            self.finished_with_success.emit(exitos, total)
            self.log_message.emit(f"🏁 Proceso finalizado ({exitos}/{total})")

        except Exception as e:
            error_msg = f"🔥 Error crítico en hilo de generación: {e}"
            self.logger.critical(error_msg)
            self.logger.debug(traceback.format_exc())
            self.error_occurred.emit(error_msg)

class FragmentoGenerarScreen(QWidget):
    """Pantalla para generar fragmentos desde marcas de video"""
    def __init__(self, logger=None, data_context=None, parent=None):
        super().__init__(parent)
        self.logger = logger or logging.getLogger(__name__)
        self.parent_window = parent
        self.videos_data = []
        self.data_context = data_context or {"videos": [], "marcas": {}, "fragmentos": []}
        self.current_video = None
        self.marcas_obj = None
        self.setup_ui()
        self.load_videos_data()

    # ------------------------------------------------------------------
    # UI Principal
    # ------------------------------------------------------------------
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 20, 30, 20)

        # Header
        header_frame = self.create_header_frame()
        main_layout.addWidget(header_frame)

        # Cuerpo con Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background: #4caf50;
                width: 3px;
                border-radius: 1px;
            }
            QSplitter::handle:hover { background: #388e3c; }
        """)

        left_panel = self.create_videos_list_panel()
        right_panel = self.create_generation_panel()

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([500, 400])
        main_layout.addWidget(splitter, stretch=1)

        # Progreso y Log
        main_layout.addWidget(self.create_progress_frame())
        main_layout.addWidget(self.create_log_frame())

    def create_header_frame(self):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(76, 175, 80, 0.1),
                    stop:1 rgba(76, 175, 80, 0.05));
                border-radius: 20px;
                border: 2px solid rgba(76, 175, 80, 0.3);
                padding: 20px;
            }
        """)
        layout = QVBoxLayout(frame)
        title = QLabel("✂️ Generador de Fragmentos")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #1b5e20;")
        title.setAlignment(Qt.AlignCenter)

        desc = QLabel("Genere automáticamente fragmentos según las marcas de preguntas detectadas")
        desc.setFont(QFont("Segoe UI", 12))
        desc.setStyleSheet("color: #2e7d32;")
        desc.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(desc)
        return frame

    # ------------------------------------------------------------------
    # Panel Izquierdo - Lista de Videos
    # ------------------------------------------------------------------
    def create_videos_list_panel(self):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                border: 2px solid #c8e6c9;
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("🎬 Videos Disponibles")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header.setStyleSheet("color: #1b5e20;")
        layout.addWidget(header)

        toolbar = QHBoxLayout()
        btn_refresh = QPushButton("🔄 Actualizar")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4caf50, stop:1 #388e3c);
                color: white; border: none; border-radius: 10px;
                padding: 8px 16px; font-weight: bold;
            }
            QPushButton:hover { background: #45a049; }
        """)
        btn_refresh.clicked.connect(self.load_videos_data)

        self.status_label = QLabel("Cargando videos...")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        toolbar.addWidget(btn_refresh)
        toolbar.addWidget(self.status_label)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.videos_table = QTableWidget()
        self.videos_table.setColumnCount(5)
        self.videos_table.setHorizontalHeaderLabels([
            "📁 Archivo", "⏱️ Duración", "❓ Marcas", "📂 Fragmentos", "📅 Modificación"
        ])
        self.videos_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 5):
            self.videos_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)

        self.videos_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.videos_table.setAlternatingRowColors(True)
        self.videos_table.clicked.connect(self.on_video_selected)
        self.videos_table.setStyleSheet("""
            QTableWidget { 
                color: black; 
                background-color: white; 
                alternate-background-color: #f5f5f5; 
                gridline-color: #e0e0e0; 
            }
            QTableWidget::item { 
                color: black; 
                padding: 5px; 
            }
            QHeaderView::section { 
                color: black; 
                background-color: #e8f5e8; 
                padding: 5px; 
                border: 1px solid #c8e6c9; 
            }
        """)

        layout.addWidget(self.videos_table)
        return frame

    # ------------------------------------------------------------------
    # Panel Derecho - Generación
    # ------------------------------------------------------------------
    def create_generation_panel(self):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                border: 2px solid #c8e6c9;
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("⚙️ Configuración de Generación")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header.setStyleSheet("color: #1b5e20;")
        layout.addWidget(header)

        self.video_info_label = QLabel("Seleccione un video para generar fragmentos.")
        self.video_info_label.setWordWrap(True)
        self.video_info_label.setStyleSheet("color: black;")
        layout.addWidget(self.video_info_label)

        # Tabla de marcas
        self.marks_table = QTableWidget()
        self.marks_table.setColumnCount(5)
        self.marks_table.setHorizontalHeaderLabels([
            "Pregunta", "Inicio (s)", "Fin (s)", "Duración (s)", "Nota"
        ])
        self.marks_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.marks_table.setStyleSheet("""
            QTableWidget { 
                color: black; 
                background-color: white; 
                alternate-background-color: #f5f5f5; 
                gridline-color: #e0e0e0; 
            }
            QTableWidget::item { 
                color: black; 
                padding: 5px; 
            }
            QHeaderView::section { 
                color: black; 
                background-color: #e8f5e8; 
                padding: 5px; 
                border: 1px solid #c8e6c9; 
            }
        """)
        layout.addWidget(self.marks_table)

        # Botón generar
        self.btn_generar = QPushButton("✂️ Generar Todos los Fragmentos")
        self.btn_generar.setEnabled(False)
        self.btn_generar.clicked.connect(self.generar_fragmentos)
        self.btn_generar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4caf50, stop:1 #388e3c);
                color: white; border-radius: 12px;
                padding: 12px 24px; font-weight: bold;
            }
            QPushButton:disabled { background: #9e9e9e; color: #ccc; }
        """)
        layout.addWidget(self.btn_generar)
        layout.addStretch()
        return frame

    # ------------------------------------------------------------------
    # Panel Inferior - Progreso y Log
    # ------------------------------------------------------------------
    def create_progress_frame(self):
        frame = QFrame()
        layout = QHBoxLayout(frame)
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        return frame

    def create_log_frame(self):
        frame = QFrame()
        layout = QVBoxLayout(frame)
        label = QLabel("📝 Registro del Proceso")
        label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        label.setStyleSheet("color: #1b5e20;")
        layout.addWidget(label)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("color: black; background-color: white;")
        layout.addWidget(self.log_output)
        return frame

    # ------------------------------------------------------------------
    # Lógica de Carga y Procesamiento
    # ------------------------------------------------------------------
    def load_videos_data(self):
        try:
            self.status_label.setText("Buscando videos...")
            videos_path = Path("data/videos_originales")
            if not videos_path.exists():
                self.show_error("El directorio de videos no existe")
                return

            video_files = list(videos_path.glob("*.mp4")) + list(videos_path.glob("*.mov")) + list(videos_path.glob("*.avi"))
            if not video_files:
                self.show_warning("No se encontraron videos.")
                self.videos_data = []
                return

            self.videos_data = [self.process_video_file(v) for v in video_files if v.exists()]
            self.update_videos_table()
            self.status_label.setText(f"✅ {len(self.videos_data)} videos cargados")

        except Exception as e:
            self.show_error(f"Error al cargar videos: {e}")
            self.logger.error(traceback.format_exc())

    def process_video_file(self, video_path: Path):
        try:
            stat = video_path.stat()
            duration = self.get_video_duration(video_path)
            marks_info = self.get_marks_info(video_path)
            fragments_dir = Path(f"data/fragmentos/{marks_info['entrevista_id']}")
            fragments_count = len(list(fragments_dir.glob("*.mp4"))) if fragments_dir.exists() else 0
            return {
                'path': video_path,
                'name': video_path.name,
                'duration': duration,
                'modification_time': datetime.fromtimestamp(stat.st_mtime),
                'marks_count': marks_info['count'],
                'marks_details': marks_info['details'],
                'entrevista_id': marks_info['entrevista_id'],
                'fragments_count': fragments_count,
            }
        except Exception as e:
            self.logger.error(f"Error procesando {video_path}: {e}")
            return None

    def get_video_duration(self, video_path: Path):
        try:
            cap = cv2.VideoCapture(str(video_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            cap.release()
            return f"{int(frames/fps//60)}:{int(frames/fps%60):02d}" if fps > 0 else "N/A"
        except Exception:
            return "N/A"

    def get_marks_info(self, video_path: Path):
        try:
            entrevista_id = video_path.stem.replace('interview_', '')
            marks_path = Path(f"data/marcas/marcas_{entrevista_id}.json")
            if not marks_path.exists():
                return {'count': 0, 'details': [], 'entrevista_id': entrevista_id}

            with open(marks_path, 'r', encoding='utf-8') as f:
                marks_data = json.load(f)

            details = []
            for m in marks_data.get('marcas', []):
                details.append({
                    'pregunta_id': m.get('pregunta_id', 'N/A'),
                    'inicio': m.get('inicio', 0),
                    'fin': m.get('fin', 0),
                    'duracion': round(m.get('fin', 0) - m.get('inicio', 0), 2),
                    'nota': m.get('nota', '')
                })
            return {'count': len(details), 'details': details, 'entrevista_id': entrevista_id}
        except Exception as e:
            self.logger.error(f"Error leyendo marcas: {e}")
            return {'count': 0, 'details': [], 'entrevista_id': 'N/A'}

    # ------------------------------------------------------------------
    # Interacción UI
    # ------------------------------------------------------------------
    def update_videos_table(self):
        self.videos_table.setRowCount(len(self.videos_data))
        for row, video in enumerate(self.videos_data):
            item0 = QTableWidgetItem(video['name'])
            item0.setForeground(Qt.GlobalColor.black)
            self.videos_table.setItem(row, 0, item0)
            item1 = QTableWidgetItem(video['duration'])
            item1.setForeground(Qt.GlobalColor.black)
            self.videos_table.setItem(row, 1, item1)
            item2 = QTableWidgetItem(str(video['marks_count']))
            item2.setForeground(Qt.GlobalColor.black)
            self.videos_table.setItem(row, 2, item2)
            item3 = QTableWidgetItem(str(video['fragments_count']))
            if video['fragments_count'] > 0:
                item3.setForeground(Qt.GlobalColor.green)
            else:
                item3.setForeground(Qt.GlobalColor.gray)
            self.videos_table.setItem(row, 3, item3)
            item4 = QTableWidgetItem(video['modification_time'].strftime("%Y-%m-%d %H:%M"))
            item4.setForeground(Qt.GlobalColor.black)
            self.videos_table.setItem(row, 4, item4)
            
            # Marcar fila en verde claro si tiene fragmentos
            if video['fragments_count'] > 0:
                light_green = QColor(240, 255, 240)
                for col in range(self.videos_table.columnCount()):
                    item = self.videos_table.item(row, col)
                    if item:
                        item.setBackground(light_green)

    def on_video_selected(self, index):
        row = index.row()
        if 0 <= row < len(self.videos_data):
            video = self.videos_data[row]
            self.current_video = video
            self.show_video_details(video)
            self.btn_generar.setEnabled(video['marks_count'] > 0)
            self.load_marcas_object(video)

    def show_video_details(self, video):
        self.video_info_label.setText(
            f"🎥 <b>{video['name']}</b><br>"
            f"⏱️ {video['duration']} | ❓ {video['marks_count']} marcas | 📂 {video['fragments_count']} fragmentos"
        )
        self.marks_table.setRowCount(len(video['marks_details']))
        for i, m in enumerate(video['marks_details']):
            item0 = QTableWidgetItem(str(m['pregunta_id']))
            item0.setForeground(Qt.GlobalColor.black)
            self.marks_table.setItem(i, 0, item0)
            item1 = QTableWidgetItem(str(m['inicio']))
            item1.setForeground(Qt.GlobalColor.black)
            self.marks_table.setItem(i, 1, item1)
            item2 = QTableWidgetItem(str(m['fin']))
            item2.setForeground(Qt.GlobalColor.black)
            self.marks_table.setItem(i, 2, item2)
            item3 = QTableWidgetItem(str(m['duracion']))
            item3.setForeground(Qt.GlobalColor.black)
            self.marks_table.setItem(i, 3, item3)
            item4 = QTableWidgetItem(m['nota'] or "")
            item4.setForeground(Qt.GlobalColor.black)
            self.marks_table.setItem(i, 4, item4)

    # ------------------------------------------------------------------
    # Generación de Fragmentos
    # ------------------------------------------------------------------
    def load_marcas_object(self, video):
        try:
            entrevista_id = video['entrevista_id']
            marcas_path = Path(f"data/marcas/marcas_{entrevista_id}.json")
            if marcas_path.exists():
                self.marcas_obj = Marcas(entrevista_id, video['path'])
                self.marcas_obj.importar_json(marcas_path)
                self.logger.info(f"Marcas cargadas para {entrevista_id}")
        except Exception as e:
            self.logger.error(f"Error cargando Marcas: {e}")

    def generar_fragmentos(self):
        if not self.current_video or not self.marcas_obj:
            self.show_warning("Seleccione un video válido con marcas.")
            return

        fragmentos_dir = Path(f"data/fragmentos/{self.current_video['entrevista_id']}")
        fragmentos_dir.mkdir(parents=True, exist_ok=True)

        self.log_output.clear()
        self.log_output.append(f"🚀 Iniciando generación de fragmentos para {self.current_video['name']}")

        self.thread = GenerationThread(self.current_video['path'], self.marcas_obj, fragmentos_dir)
        self.thread.progress_updated.connect(self.progress.setValue)
        self.thread.log_message.connect(self.log_output.append)
        self.thread.finished_with_success.connect(self.on_generation_finished)
        self.thread.error_occurred.connect(self.on_generation_error)
        self.thread.start()
        self.btn_generar.setEnabled(False)

    def on_generation_finished(self, exitos, total):
        msg_text = f"🏁 Generación completada: {exitos}/{total} fragmentos creados."
        self.log_output.append(msg_text)
        self.logger.info(msg_text)
        self.btn_generar.setEnabled(True)

        # ✅ Mantener referencia viva del hilo hasta después del diálogo
        thread_ref = self.thread

        msgbox = QMessageBox(self)
        msgbox.setWindowTitle("Proceso Finalizado")
        msgbox.setText(msg_text)
        msgbox.setIcon(QMessageBox.Information)
        msgbox.setStyleSheet("""
            QLabel { 
                color: black; 
                background-color: white; 
            }
        """)
        msgbox.exec()

        # ✅ Limpiar correctamente el hilo
        if thread_ref:
            thread_ref.quit()
            thread_ref.wait()
            thread_ref.deleteLater()
            self.thread = None

        # ✅ Recargar tabla de forma segura (tras liberar el hilo)
        self.load_videos_data()

    def on_generation_error(self, msg_text):
        self.log_output.append(f"❌ {msg_text}")
        self.logger.error(msg_text)
        self.btn_generar.setEnabled(True)
        
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Error")
        msgbox.setText(msg_text)
        msgbox.setIcon(QMessageBox.Critical)
        msgbox.setStyleSheet("""
            QLabel { 
                color: black; 
                background-color: white; 
            }
        """)
        msgbox.exec()

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def show_error(self, msg):
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Error")
        msgbox.setText(msg)
        msgbox.setIcon(QMessageBox.Critical)
        msgbox.setStyleSheet("""
            QLabel { 
                color: black; 
                background-color: white; 
            }
        """)
        msgbox.exec()
        self.logger.error(msg)

    def show_warning(self, msg):
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Advertencia")
        msgbox.setText(msg)
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setStyleSheet("""
            QLabel { 
                color: black; 
                background-color: white; 
            }
        """)
        msgbox.exec()
        self.logger.warning(msg)