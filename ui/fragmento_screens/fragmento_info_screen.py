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
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter
import cv2
import subprocess

# Importar las clases de marcas
from classes.marca import Marca
from classes.marcas import Marcas


class FragmentoInfoScreen(QWidget):
    def __init__(self, logger = None, data_context= None,parent=None):
        super().__init__(parent)
        self.logger = logger or logging.getLogger(__name__)
        self.parent_window = parent
        self.videos_data = []
        self.data_context = data_context or {"videos": [], "marcas": {}, "fragmentos": []}
        self.setup_ui()
        self.load_videos_data()
        
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 20, 30, 20)

        # 🔸 Header de la pantalla
        header_frame = self.create_header_frame()
        main_layout.addWidget(header_frame)

        # 🔸 Contenido principal con splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background: #4caf50;
                width: 3px;
                border-radius: 1px;
            }
            QSplitter::handle:hover {
                background: #388e3c;
            }
        """)

        # Panel izquierdo - Lista de videos
        left_panel = self.create_videos_list_panel()
        splitter.addWidget(left_panel)

        # Panel derecho - Detalles del video
        right_panel = self.create_video_details_panel()
        splitter.addWidget(right_panel)

        # Configurar proporciones del splitter
        splitter.setSizes([500, 400])
        main_layout.addWidget(splitter, stretch=1)

        # 🔸 Barra de estado
        status_frame = self.create_status_frame()
        main_layout.addWidget(status_frame)

    def create_header_frame(self):
        """Crear el header de la pantalla"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(76, 175, 80, 0.1),
                    stop:1 rgba(76, 175, 80, 0.05));
                border-radius: 20px;
                border: 2px solid rgba(76, 175, 80, 0.3);
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(10)

        # Título
        title = QLabel("📹 Información de Videos Originales")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #1b5e20;")
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)

        # Descripción
        desc = QLabel("Resumen completo del material disponible para fragmentación")
        desc.setFont(QFont("Segoe UI", 12))
        desc.setStyleSheet("color: #2e7d32;")
        desc.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(desc)

        return header_frame

    def create_videos_list_panel(self):
        """Crear el panel de lista de videos"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                border: 2px solid #c8e6c9;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header del panel
        panel_header = QLabel("🎬 Videos Disponibles")
        panel_header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        panel_header.setStyleSheet("color: #1b5e20; margin-bottom: 10px;")
        layout.addWidget(panel_header)

        # Barra de herramientas
        toolbar = QHBoxLayout()
        
        btn_refresh = QPushButton("🔄 Actualizar")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4caf50, stop:1 #388e3c);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5cb860, stop:1 #4caf50);
            }
            QPushButton:pressed {
                background: #2e7d32;
            }
        """)
        btn_refresh.clicked.connect(self.load_videos_data)
        
        self.status_label = QLabel("Cargando videos...")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")

        toolbar.addWidget(btn_refresh)
        toolbar.addWidget(self.status_label)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Tabla de videos
        self.videos_table = QTableWidget()
        self.videos_table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #c8e6c9;
                border-radius: 10px;
                gridline-color: #e8f5e9;
                selection-background-color: #c8e6c9;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e8f5e9;
                color: #000000;
            }
            QTableWidget::item:selected {
                background: #a5d6a7;
                color: #000000;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e8f5e9, stop:1 #c8e6c9);
                color: #1b5e20;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-right: 1px solid #a5d6a7;
            }
        """)
        self.videos_table.setColumnCount(5)
        self.videos_table.setHorizontalHeaderLabels([
            "📁 Archivo", "⏱️ Duración", "📊 Tamaño", "❓ Marcas", "📅 Modificación"
        ])
        self.videos_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.videos_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.videos_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.videos_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.videos_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.videos_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.videos_table.setAlternatingRowColors(True)
        self.videos_table.clicked.connect(self.on_video_selected)
        
        layout.addWidget(self.videos_table)

        return panel

    def create_video_details_panel(self):
        """Crear el panel de detalles del video"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                border: 2px solid #c8e6c9;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header del panel
        panel_header = QLabel("🔍 Detalles del Video")
        panel_header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        panel_header.setStyleSheet("color: #1b5e20; margin-bottom: 10px;")
        layout.addWidget(panel_header)

        # Información básica
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background: #f1f8e9;
                border-radius: 10px;
                border: 1px solid #c8e6c9;
                padding: 15px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        self.details_name = QLabel("Seleccione un video")
        self.details_name.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.details_name.setStyleSheet("color: #1b5e20; margin-bottom: 10px;")
        
        self.details_info = QLabel("")
        self.details_info.setFont(QFont("Segoe UI", 10))
        self.details_info.setStyleSheet("color: #2e7d32; line-height: 1.4;")
        self.details_info.setWordWrap(True)
        
        info_layout.addWidget(self.details_name)
        info_layout.addWidget(self.details_info)
        layout.addWidget(info_frame)

        # Botón para reproducir video completo
        play_button = QPushButton("▶️ Reproducir Video Completo")
        play_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4caf50, stop:1 #388e3c);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5cb860, stop:1 #4caf50);
            }
            QPushButton:pressed {
                background: #2e7d32;
            }
        """)
        play_button.clicked.connect(self.play_full_video)
        self.play_button = play_button
        layout.addWidget(play_button)

        # Información de marcas
        marks_frame = QFrame()
        marks_frame.setStyleSheet("""
            QFrame {
                background: #e8f5e9;
                border-radius: 10px;
                border: 1px solid #a5d6a7;
                padding: 15px;
            }
        """)
        marks_layout = QVBoxLayout(marks_frame)
        
        marks_header = QLabel("📋 Marcas y Preguntas")
        marks_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        marks_header.setStyleSheet("color: #1b5e20; margin-bottom: 10px;")
        marks_layout.addWidget(marks_header)
        
        self.marks_info = QLabel("No hay marcas disponibles")
        self.marks_info.setFont(QFont("Segoe UI", 10))
        self.marks_info.setStyleSheet("color: #388e3c; line-height: 1.4;")
        self.marks_info.setWordWrap(True)
        marks_layout.addWidget(self.marks_info)
        
        layout.addWidget(marks_frame)

        # Área de notas
        notes_frame = QFrame()
        notes_frame.setStyleSheet("""
            QFrame {
                background: #fafafa;
                border-radius: 10px;
                border: 1px solid #bdbdbd;
                padding: 15px;
            }
        """)
        notes_layout = QVBoxLayout(notes_frame)
        
        notes_header = QLabel("📝 Notas del Video")
        notes_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        notes_header.setStyleSheet("color: #1b5e20; margin-bottom: 10px;")
        notes_layout.addWidget(notes_header)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Agregue notas o comentarios sobre este video...")
        self.notes_edit.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 1px solid #c8e6c9;
                border-radius: 8px;
                padding: 10px;
                font-size: 10px;
            }
        """)
        self.notes_edit.textChanged.connect(self.on_notes_changed)
        notes_layout.addWidget(self.notes_edit)
        
        layout.addWidget(notes_frame)

        layout.addStretch()

        return panel

    def play_full_video(self):
        """Reproducir el video completo seleccionado"""
        current_row = self.videos_table.currentRow()
        if current_row >= 0 and current_row < len(self.videos_data):
            video_path = self.videos_data[current_row]['path']
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(str(video_path))
                elif os.name == 'posix':  # macOS/Linux
                    subprocess.run(['open', str(video_path)] if os.uname().sysname == 'Darwin' else ['xdg-open', str(video_path)])
                self.logger.info(f"Reproduciendo video: {video_path}")
            except Exception as e:
                self.show_error(f"No se pudo reproducir el video: {str(e)}")
        else:
            self.show_warning("Seleccione un video primero")

    def create_status_frame(self):
        """Crear la barra de estado"""
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background: rgba(232, 245, 233, 0.8);
                border-radius: 10px;
                border: 1px solid #a5d6a7;
                padding: 10px;
            }
        """)
        layout = QHBoxLayout(status_frame)
        
        self.summary_label = QLabel("Total de videos: 0")
        self.summary_label.setStyleSheet("color: #2e7d32; font-weight: bold;")
        
        layout.addWidget(self.summary_label)
        layout.addStretch()
        
        return status_frame

    def load_videos_data(self):
        """Cargar y procesar todos los videos del directorio"""
        try:
            self.status_label.setText("Buscando videos...")
            videos_path = Path("data/videos_originales")
            
            if not videos_path.exists():
                self.show_error("El directorio de videos no existe")
                return

            video_files = list(videos_path.glob("*.mp4")) + list(videos_path.glob("*.avi")) + list(videos_path.glob("*.mov"))
            
            if not video_files:
                self.show_warning("No se encontraron videos en el directorio")
                self.videos_data = []
                self.update_videos_table()
                return

            self.videos_data = []
            self.status_label.setText(f"Procesando {len(video_files)} videos...")
            
            for i, video_file in enumerate(video_files):
                try:
                    video_info = self.process_video_file(video_file)
                    if video_info:
                        self.videos_data.append(video_info)
                except Exception as e:
                    print(f"Error procesando {video_file.name}: {str(e)}")
                    continue

            self.update_videos_table()
            self.status_label.setText(f"✅ {len(self.videos_data)} videos cargados")
            
        except Exception as e:
            self.show_error(f"Error al cargar videos: {str(e)}")

    def process_video_file(self, video_path: Path):
        """Procesar un archivo de video individual"""
        try:
            # Información básica del archivo
            stat = video_path.stat()
            file_size = stat.st_size
            modification_time = datetime.fromtimestamp(stat.st_mtime)
            
            # Obtener duración del video
            duration = self.get_video_duration(video_path)
            
            # Obtener información de marcas
            marks_info = self.get_marks_info(video_path)
            
            return {
                'path': video_path,
                'name': video_path.name,
                'duration': duration,
                'file_size': file_size,
                'modification_time': modification_time,
                'marks_count': marks_info['count'],
                'marks_details': marks_info['details'],
                'entrevista_id': marks_info['entrevista_id'],
                'notes': ""
            }
            
        except Exception as e:
            print(f"Error procesando {video_path}: {str(e)}")
            return None

    def get_video_duration(self, video_path: Path):
        """Obtener la duración del video usando OpenCV"""
        try:
            cap = cv2.VideoCapture(str(video_path))
            if cap.isOpened():
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                cap.release()
                
                if fps > 0 and frame_count > 0:
                    duration_seconds = frame_count / fps
                    return self.format_duration(duration_seconds)
            return "N/A"
        except:
            return "N/A"

    def get_marks_info(self, video_path: Path):
        """Obtener información de las marcas asociadas al video"""
        try:
            # Extraer entrevista_id del nombre del archivo (asumiendo formato: interview_{id}.mp4)
            video_name = video_path.stem
            entrevista_id = video_name.replace('interview_', '') if 'interview_' in video_name else video_name
            
            marks_path = Path(f"data/marcas/marcas_{entrevista_id}.json")
            
            if not marks_path.exists():
                return {'count': 0, 'details': [], 'entrevista_id': entrevista_id}
            
            # Cargar marcas desde JSON
            with open(marks_path, 'r', encoding='utf-8') as f:
                marks_data = json.load(f)
            
            marks_details = []
            for marca in marks_data.get('marcas', []):
                marks_details.append({
                    'pregunta_id': marca.get('pregunta_id', 'N/A'),
                    'inicio': marca.get('inicio', 'N/A'),
                    'fin': marca.get('fin', 'N/A'),
                    'duracion': marca.get('fin', 0) - marca.get('inicio', 0) if marca.get('fin') else 'N/A',
                    'nota': marca.get('nota', '')
                })
            
            return {
                'count': len(marks_details),
                'details': marks_details,
                'entrevista_id': entrevista_id
            }
            
        except Exception as e:
            print(f"Error cargando marcas para {video_path}: {str(e)}")
            return {'count': 0, 'details': [], 'entrevista_id': 'N/A'}

    def update_videos_table(self):
        """Actualizar la tabla con los datos de los videos"""
        self.videos_table.setRowCount(len(self.videos_data))
        
        for row, video in enumerate(self.videos_data):
            # Nombre del archivo
            name_item = QTableWidgetItem(video['name'])
            name_item.setData(Qt.UserRole, row)  # Guardar índice para referencia
            
            # Duración
            duration_item = QTableWidgetItem(video['duration'])
            
            # Tamaño del archivo
            size_item = QTableWidgetItem(self.format_file_size(video['file_size']))
            
            # Número de marcas
            marks_item = QTableWidgetItem(str(video['marks_count']))
            if video['marks_count'] > 0:
                marks_item.setForeground(Qt.darkGreen)
            else:
                marks_item.setForeground(Qt.darkRed)
            
            # Fecha de modificación
            date_item = QTableWidgetItem(video['modification_time'].strftime("%Y-%m-%d %H:%M"))
            
            self.videos_table.setItem(row, 0, name_item)
            self.videos_table.setItem(row, 1, duration_item)
            self.videos_table.setItem(row, 2, size_item)
            self.videos_table.setItem(row, 3, marks_item)
            self.videos_table.setItem(row, 4, date_item)
        
        # Actualizar resumen
        total_size = sum(video['file_size'] for video in self.videos_data)
        total_marks = sum(video['marks_count'] for video in self.videos_data)
        self.summary_label.setText(
            f"📊 Total: {len(self.videos_data)} videos | "
            f"📁 Tamaño total: {self.format_file_size(total_size)} | "
            f"❓ Marcas: {total_marks}"
        )

    def on_video_selected(self, index):
        """Manejar la selección de un video en la tabla"""
        row = index.row()
        if 0 <= row < len(self.videos_data):
            video = self.videos_data[row]
            self.show_video_details(video)

    def on_notes_changed(self):
        """Manejar cambios en las notas"""
        current_row = self.videos_table.currentRow()
        if 0 <= current_row < len(self.videos_data):
            self.videos_data[current_row]['notes'] = self.notes_edit.toPlainText()
    
    def show_video_details(self, video):
        """Mostrar detalles del video seleccionado"""
        # Información básica
        self.details_name.setText(f"🎬 {video['name']}")
        
        basic_info = f"""
        📅 <b>Fecha de modificación:</b> {video['modification_time'].strftime("%Y-%m-%d %H:%M:%S")}<br>
        ⏱️ <b>Duración:</b> {video['duration']}<br>
        📊 <b>Tamaño:</b> {self.format_file_size(video['file_size'])}<br>
        🆔 <b>ID Entrevista:</b> {video['entrevista_id']}<br>
        📍 <b>Ruta:</b> {video['path']}
        """
        self.details_info.setText(basic_info)
        
        # Ocultar/mostrar botón de reproducción según si hay video seleccionado
        self.play_button.setVisible(True)
        
        # Información de marcas
        if video['marks_count'] > 0:
            marks_text = f"<b>Total de marcas/preguntas:</b> {video['marks_count']}<br><br>"
            for i, marca in enumerate(video['marks_details'][:10]):  # Mostrar máximo 10
                marks_text += f"""
                <b>Pregunta {marca['pregunta_id']}:</b> 
                ⏰ {marca['inicio']}s - {marca['fin']}s 
                (⏱️ {marca['duracion']:.1f}s)<br>
                """
            if video['marks_count'] > 10:
                marks_text += f"... y {video['marks_count'] - 10} marcas más"
        else:
            marks_text = "No se encontraron marcas para este video.<br>Puede agregar marcas en el módulo de generación de fragmentos."
        
        self.marks_info.setText(marks_text)
        
        # Notas: Concatenar comentarios de las marcas si existen
        marks_comments = ""
        if video['marks_details']:
            marks_comments = "Comentarios de las marcas:\n\n"
            for marca in video['marks_details']:
                if marca['nota']:
                    marks_comments += f"Pregunta {marca['pregunta_id']}:\n{marca['nota']}\n\n"
        
        # Cargar notas existentes + comentarios de marcas
        existing_notes = video.get('notes', '')
        full_notes = f"{marks_comments}\n{existing_notes}" if existing_notes else marks_comments
        
        self.notes_edit.blockSignals(True)
        self.notes_edit.setText(full_notes)
        self.notes_edit.blockSignals(False)
        self.notes_edit.setStyleSheet("""
        QTextEdit {
            background: white;
            border: 1px solid #c8e6c9;
            border-radius: 8px;
            padding: 10px;
            font-size: 10px;
            color: #000000;
        }
    """)

    def format_duration(self, seconds):
        """Formatear duración en segundos a formato legible"""
        if seconds == "N/A":
            return "N/A"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def format_file_size(self, size_bytes):
        """Formatear tamaño de archivo a formato legible"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"

    def show_error(self, message):
        """Mostrar mensaje de error"""
        QMessageBox.critical(self, "Error", message)
        self.logger.error(message)
        self.status_label.setText("❌ Error al cargar videos")

    def show_warning(self, message):
        """Mostrar mensaje de advertencia"""
        QMessageBox.warning(self, "Advertencia", message)
        self.logger.warning(message)
        self.status_label.setText("⚠️ No hay videos disponibles")

    def refresh_data(self):
        """Método público para refrescar los datos"""
        self.logger.info("Refrescando datos de videos...")
        self.load_videos_data()