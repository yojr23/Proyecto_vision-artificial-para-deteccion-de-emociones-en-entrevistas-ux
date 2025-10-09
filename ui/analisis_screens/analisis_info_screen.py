import os
import json
import logging
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QFrame,
    QTextEdit, QSplitter, QMessageBox, QProgressBar,
    QComboBox, QListWidget, QListWidgetItem, QGroupBox,
    QFileDialog, QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap, QPainter
import cv2
import subprocess


class AnalisisInfoScreen(QWidget):
    """Pantalla para mostrar información de fragmentos antes del análisis"""
    def __init__(self, logger=None, data_context=None, parent=None):
        super().__init__(parent)
        self.logger = logger or logging.getLogger(__name__)
        self.parent_window = parent
        self.data_context = data_context or {}
        self.current_entrevista = None
        self.fragmentos_data = []
        self.setup_ui()
        self.cargar_entrevistas()

    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 20, 30, 20)

        # 🔸 Header de la pantalla
        header_frame = self.create_header_frame()
        main_layout.addWidget(header_frame)

        # 🔸 Panel de selección de entrevista
        selection_frame = self.create_selection_frame()
        main_layout.addWidget(selection_frame)

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

        # Panel izquierdo - Lista de fragmentos
        left_panel = self.create_fragmentos_list_panel()
        splitter.addWidget(left_panel)

        # Panel derecho - Detalles y estadísticas
        right_panel = self.create_details_panel()
        splitter.addWidget(right_panel)

        # Configurar proporciones del splitter
        splitter.setSizes([400, 500])
        main_layout.addWidget(splitter, stretch=1)

        # 🔸 Barra de estado y botones de acción
        action_frame = self.create_action_frame()
        main_layout.addWidget(action_frame)

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
            QLabel {
                color: #000000;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(10)

        # Título
        title = QLabel("📊 Información para Análisis de Fragmentos")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)

        # Descripción
        desc = QLabel("Revise la información de los fragmentos antes de proceder con el análisis de emociones")
        desc.setFont(QFont("Segoe UI", 12))
        desc.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(desc)

        return header_frame

    def create_selection_frame(self):
        """Crear panel de selección de entrevista"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                border: 2px solid #c8e6c9;
                padding: 15px;
            }
            QLabel {
                color: #000000;
            }
        """)
        layout = QHBoxLayout(frame)

        # Label
        label = QLabel("📋 Seleccionar Entrevista:")
        label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(label)

        # ComboBox para entrevistas
        self.entrevista_combo = QComboBox()
        self.entrevista_combo.setFont(QFont("Segoe UI", 11))
        self.entrevista_combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: 2px solid #4caf50;
                border-radius: 8px;
                padding: 8px 12px;
                color: #000000;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #4caf50;
                margin-right: 10px;
            }
        """)
        self.entrevista_combo.currentTextChanged.connect(self.on_entrevista_selected)
        layout.addWidget(self.entrevista_combo)

        # Botón actualizar
        btn_refresh = QPushButton("🔄 Actualizar Lista")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4caf50, stop:1 #388e3c);
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5cb860, stop:1 #4caf50);
            }
        """)
        btn_refresh.clicked.connect(self.cargar_entrevistas)
        layout.addWidget(btn_refresh)

        layout.addStretch()

        return frame

    def create_fragmentos_list_panel(self):
        """Crear panel de lista de fragmentos"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                border: 2px solid #c8e6c9;
            }
            QLabel {
                color: #000000;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header del panel
        panel_header = QLabel("📁 Fragmentos Disponibles para Análisis")
        panel_header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        panel_header.setStyleSheet("margin-bottom: 10px;")
        layout.addWidget(panel_header)

        # Tabla de fragmentos
        self.fragmentos_table = QTableWidget()
        self.fragmentos_table.setColumnCount(5)
        self.fragmentos_table.setHorizontalHeaderLabels([
            "🎬 Fragmento", "⏱️ Duración", "📊 Tamaño", "📅 Creación", "❓ Pregunta ID"
        ])
        self.fragmentos_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.fragmentos_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.fragmentos_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.fragmentos_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.fragmentos_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.fragmentos_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.fragmentos_table.setAlternatingRowColors(True)
        self.fragmentos_table.clicked.connect(self.on_fragmento_selected)
        
        self.fragmentos_table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #c8e6c9;
                border-radius: 10px;
                gridline-color: #e8f5e9;
                selection-background-color: #c8e6c9;
                color: #000000;
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
                color: #000000;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-right: 1px solid #a5d6a7;
            }
        """)
        layout.addWidget(self.fragmentos_table)

        return panel

    def create_details_panel(self):
        """Crear panel de detalles y estadísticas"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                border: 2px solid #c8e6c9;
            }
            QLabel {
                color: #000000;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header del panel
        panel_header = QLabel("🔍 Información Detallada del Fragmento")
        panel_header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        panel_header.setStyleSheet("margin-bottom: 10px;")
        layout.addWidget(panel_header)

        # Información del fragmento
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
        
        self.details_name = QLabel("Seleccione un fragmento para ver los detalles")
        self.details_name.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.details_name.setStyleSheet("margin-bottom: 10px;")
        
        self.details_info = QLabel("")
        self.details_info.setFont(QFont("Segoe UI", 10))
        self.details_info.setStyleSheet("line-height: 1.4;")
        self.details_info.setWordWrap(True)
        
        info_layout.addWidget(self.details_name)
        info_layout.addWidget(self.details_info)
        layout.addWidget(info_frame)

        # Información de la marca original
        marca_frame = QFrame()
        marca_frame.setStyleSheet("""
            QFrame {
                background: #e8f5e9;
                border-radius: 10px;
                border: 1px solid #a5d6a7;
                padding: 15px;
            }
        """)
        marca_layout = QVBoxLayout(marca_frame)
        
        marca_header = QLabel("📋 Información de la Marca Original")
        marca_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        marca_header.setStyleSheet("margin-bottom: 10px;")
        marca_layout.addWidget(marca_header)
        
        self.marca_info = QLabel("No hay información de marca disponible")
        self.marca_info.setFont(QFont("Segoe UI", 10))
        self.marca_info.setStyleSheet("line-height: 1.4;")
        self.marca_info.setWordWrap(True)
        marca_layout.addWidget(self.marca_info)
        
        layout.addWidget(marca_frame)

        # Estadísticas de la entrevista
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background: #e3f2fd;
                border-radius: 10px;
                border: 1px solid #90caf9;
                padding: 15px;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        
        stats_header = QLabel("📈 Estadísticas de la Entrevista")
        stats_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        stats_header.setStyleSheet("margin-bottom: 10px;")
        stats_layout.addWidget(stats_header)
        
        self.stats_info = QLabel("Seleccione una entrevista para ver las estadísticas")
        self.stats_info.setFont(QFont("Segoe UI", 10))
        self.stats_info.setStyleSheet("line-height: 1.4;")
        self.stats_info.setWordWrap(True)
        stats_layout.addWidget(self.stats_info)
        
        layout.addWidget(stats_frame)

        layout.addStretch()
        return panel

    def create_action_frame(self):
        """Crear frame con botones de acción"""
        action_frame = QFrame()
        action_frame.setStyleSheet("""
            QFrame {
                background: rgba(232, 245, 233, 0.8);
                border-radius: 15px;
                border: 1px solid #a5d6a7;
                padding: 15px;
            }
            QLabel {
                color: #000000;
            }
        """)
        layout = QHBoxLayout(action_frame)
        
        # Información de resumen
        self.summary_label = QLabel("Seleccione una entrevista para ver los fragmentos disponibles")
        self.summary_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.summary_label)
        
        layout.addStretch()
        
        # Botón para proceder al análisis
        self.btn_analizar = QPushButton("🚀 Proceder al Análisis de Emociones")
        self.btn_analizar.setEnabled(False)
        self.btn_analizar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4caf50, stop:1 #388e3c);
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:disabled {
                background: #cccccc;
                color: #666666;
            }
            QPushButton:hover:enabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5cb860, stop:1 #4caf50);
            }
        """)
        self.btn_analizar.clicked.connect(self.proceder_analisis)
        layout.addWidget(self.btn_analizar)
        
        return action_frame

    def cargar_entrevistas(self):
        """Cargar lista de entrevistas disponibles"""
        try:
            fragmentos_dir = Path("data/fragmentos")
            if not fragmentos_dir.exists():
                self.entrevista_combo.clear()
                self.summary_label.setText("❌ No existe el directorio de fragmentos")
                return

            # Buscar carpetas de entrevistas
            entrevistas = [d for d in fragmentos_dir.iterdir() if d.is_dir()]
            
            self.entrevista_combo.clear()
            self.entrevista_combo.addItem("-- Seleccione una entrevista --")
            
            for entrevista in entrevistas:
                fragmentos = list(entrevista.glob("*.mp4"))
                if fragmentos:
                    self.entrevista_combo.addItem(
                        f"{entrevista.name} ({len(fragmentos)} fragmentos)"
                    )

            if len(entrevistas) == 0:
                self.summary_label.setText("ℹ️ No hay entrevistas con fragmentos generados")
            else:
                self.summary_label.setText(f"✅ {len(entrevistas)} entrevistas con fragmentos encontradas")

        except Exception as e:
            self.mostrar_error(f"Error al cargar entrevistas: {str(e)}")

    def on_entrevista_selected(self, texto):
        """Manejar selección de entrevista"""
        if texto == "-- Seleccione una entrevista --" or not texto:
            self.current_entrevista = None
            self.fragmentos_data = []
            self.actualizar_tabla_fragmentos()
            self.btn_analizar.setEnabled(False)
            self.actualizar_estadisticas()
            return

        # Extraer ID de entrevista del texto (formato: "id_entrevista (X fragmentos)")
        entrevista_id = texto.split(' ')[0]
        self.current_entrevista = entrevista_id
        self.cargar_fragmentos_entrevista(entrevista_id)
        self.btn_analizar.setEnabled(True)

    def cargar_fragmentos_entrevista(self, entrevista_id):
        """Cargar fragmentos de una entrevista específica"""
        try:
            entrevista_dir = Path("data/fragmentos") / entrevista_id
            if not entrevista_dir.exists():
                self.mostrar_error(f"No se encuentra la carpeta de la entrevista {entrevista_id}")
                return

            fragmentos_files = list(entrevista_dir.glob("*.mp4"))
            self.fragmentos_data = []

            for frag_path in fragmentos_files:
                try:
                    stat = frag_path.stat()
                    duration = self.obtener_duracion_video(frag_path)
                    
                    fragmento_info = {
                        'path': frag_path,
                        'name': frag_path.name,
                        'duration': duration,
                        'size': stat.st_size,
                        'creation_time': datetime.fromtimestamp(stat.st_ctime),
                        'modification_time': datetime.fromtimestamp(stat.st_mtime)
                    }
                    
                    # Extraer información de la marca del nombre del archivo
                    self.extraer_info_marca(fragmento_info, frag_path.name)
                    
                    self.fragmentos_data.append(fragmento_info)
                    
                except Exception as e:
                    self.logger.error(f"Error procesando {frag_path}: {str(e)}")
                    continue

            self.actualizar_tabla_fragmentos()
            self.actualizar_estadisticas()

        except Exception as e:
            self.mostrar_error(f"Error al cargar fragmentos: {str(e)}")

    def extraer_info_marca(self, fragmento_info, filename):
        """Extraer información de la marca original desde el nombre del archivo y JSON."""
        try:
            name = filename.replace(".mp4", "")
            parts = name.split("_")

            # Buscar el último elemento (pregunta_id)
            pregunta_id = parts[-1]
            entrevista_id = "_".join(parts[1:-1])  # todo lo que esté entre "fragmento" y el último valor

            fragmento_info["entrevista_id"] = entrevista_id
            fragmento_info["pregunta_id"] = pregunta_id

            # Buscar archivo de marcas
            marcas_path = Path(f"data/marcas/marcas_{entrevista_id}.json")
            if not marcas_path.exists():
                self.logger.warning(f"No se encontró archivo de marcas para {entrevista_id}")
                return

            with open(marcas_path, "r", encoding="utf-8") as f:
                marcas_data = json.load(f)

            # Buscar la marca con el mismo pregunta_id
            for marca in marcas_data.get("marcas", []):
                if str(marca.get("pregunta_id")) == str(pregunta_id):
                    fragmento_info["marca_inicio"] = marca.get("inicio", "N/A")
                    fragmento_info["marca_fin"] = marca.get("fin", "N/A")
                    fragmento_info["marca_nota"] = marca.get("nota", "")
                    break
            else:
                # Si no se encontró la marca
                self.logger.warning(f"No se encontró marca para pregunta_id {pregunta_id} en {entrevista_id}")

        except Exception as e:
            self.logger.error(f"Error al extraer información de marca para {filename}: {e}")

    def obtener_duracion_video(self, video_path):
        """Obtener duración del video usando OpenCV"""
        try:
            cap = cv2.VideoCapture(str(video_path))
            if cap.isOpened():
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                cap.release()
                
                if fps > 0 and frame_count > 0:
                    duration_seconds = frame_count / fps
                    return self.formatear_duracion(duration_seconds)
            return "N/A"
        except:
            return "N/A"

    def actualizar_tabla_fragmentos(self):
        """Actualizar la tabla con los fragmentos cargados"""
        self.fragmentos_table.setRowCount(len(self.fragmentos_data))
        
        for row, frag in enumerate(self.fragmentos_data):
            # Nombre del fragmento
            name_item = QTableWidgetItem(frag['name'])
            name_item.setData(Qt.UserRole, row)
            
            # Duración
            duration_item = QTableWidgetItem(frag['duration'])
            
            # Tamaño
            size_item = QTableWidgetItem(self.formatear_tamaño_archivo(frag['size']))
            
            # Fecha de creación
            date_item = QTableWidgetItem(frag['creation_time'].strftime("%Y-%m-%d %H:%M"))
            
            # Pregunta ID
            pregunta_item = QTableWidgetItem(frag.get('pregunta_id', 'N/A'))
            
            self.fragmentos_table.setItem(row, 0, name_item)
            self.fragmentos_table.setItem(row, 1, duration_item)
            self.fragmentos_table.setItem(row, 2, size_item)
            self.fragmentos_table.setItem(row, 3, date_item)
            self.fragmentos_table.setItem(row, 4, pregunta_item)

    def actualizar_estadisticas(self):
        """Actualizar las estadísticas de la entrevista seleccionada"""
        if not self.current_entrevista or not self.fragmentos_data:
            self.stats_info.setText("Seleccione una entrevista para ver las estadísticas")
            return

        total_fragmentos = len(self.fragmentos_data)
        total_duracion = sum(self.obtener_duracion_segundos(frag) for frag in self.fragmentos_data)
        total_tamaño = sum(frag['size'] for frag in self.fragmentos_data)
        
        stats_text = f"""
        📊 <b>Estadísticas de la Entrevista:</b><br>
        • <b>Total de fragmentos:</b> {total_fragmentos}<br>
        • <b>Duración total:</b> {self.formatear_duracion(total_duracion)}<br>
        • <b>Tamaño total:</b> {self.formatear_tamaño_archivo(total_tamaño)}<br>
        • <b>Fragmento más largo:</b> {self.obtener_fragmento_mas_largo()}<br>
        • <b>Fragmento más corto:</b> {self.obtener_fragmento_mas_corto()}<br>
        • <b>Fecha más reciente:</b> {max(frag['creation_time'] for frag in self.fragmentos_data).strftime('%Y-%m-%d %H:%M')}
        """
        
        self.stats_info.setText(stats_text)
        
        # Actualizar resumen
        self.summary_label.setText(
            f"📊 Entrevista {self.current_entrevista}: "
            f"{total_fragmentos} fragmentos | "
            f"Duración total: {self.formatear_duracion(total_duracion)} | "
            f"Tamaño: {self.formatear_tamaño_archivo(total_tamaño)}"
        )

    def obtener_duracion_segundos(self, fragmento):
        """Obtener duración en segundos para cálculos"""
        if fragmento['duration'] == "N/A":
            return 0
        
        try:
            parts = fragmento['duration'].split(':')
            if len(parts) == 3:  # HH:MM:SS
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            elif len(parts) == 2:  # MM:SS
                return int(parts[0]) * 60 + int(parts[1])
            else:
                return 0
        except:
            return 0

    def obtener_fragmento_mas_largo(self):
        """Obtener información del fragmento más largo"""
        if not self.fragmentos_data:
            return "N/A"
        
        mas_largo = max(self.fragmentos_data, key=lambda x: self.obtener_duracion_segundos(x))
        return f"{mas_largo['duration']} ({mas_largo['name']})"

    def obtener_fragmento_mas_corto(self):
        """Obtener información del fragmento más corto"""
        if not self.fragmentos_data:
            return "N/A"
        
        # Filtrar fragmentos con duración válida
        fragmentos_validos = [f for f in self.fragmentos_data if self.obtener_duracion_segundos(f) > 0]
        if not fragmentos_validos:
            return "N/A"
        
        mas_corto = min(fragmentos_validos, key=lambda x: self.obtener_duracion_segundos(x))
        return f"{mas_corto['duration']} ({mas_corto['name']})"

    def on_fragmento_selected(self, index):
        """Manejar selección de fragmento en la tabla"""
        row = index.row()
        if 0 <= row < len(self.fragmentos_data):
            fragmento = self.fragmentos_data[row]
            self.mostrar_detalles_fragmento(fragmento)
            self.logger.info(f"Fragmento seleccionado: {fragmento['name']}")

    def mostrar_detalles_fragmento(self, fragmento):
        """Mostrar detalles del fragmento seleccionado"""
        # Información básica
        self.details_name.setText(f"🎬 {fragmento['name']}")
        
        basic_info = f"""
        📅 <b>Fecha de creación:</b> {fragmento['creation_time'].strftime("%Y-%m-%d %H:%M:%S")}<br>
        ⏱️ <b>Duración:</b> {fragmento['duration']}<br>
        📊 <b>Tamaño:</b> {self.formatear_tamaño_archivo(fragmento['size'])}<br>
        📍 <b>Ruta:</b> {fragmento['path']}<br>
        🆔 <b>Entrevista:</b> {fragmento.get('entrevista_id', 'N/A')}<br>
        ❓ <b>Pregunta ID:</b> {fragmento.get('pregunta_id', 'N/A')}
        """
        self.details_info.setText(basic_info)
        
        # Información de la marca
        marca_inicio, marca_fin, marca_nota = "N/A", "N/A", "No disponible"
        try:
            entrevista_id = fragmento.get("entrevista_id")
            pregunta_id = fragmento.get("pregunta_id")
            marcas_path = Path(f"data/marcas/marcas_{entrevista_id}.json")

            if marcas_path.exists():
                with open(marcas_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for m in data.get("marcas", []):
                        try:
                            if int(m.get("pregunta_id")) == int(pregunta_id):
                                marca_inicio = m.get("inicio", "N/A")
                                marca_fin = m.get("fin", "N/A")
                                marca_nota = m.get("nota", "No disponible")
                                break
                        except ValueError:
                            continue

            else:
                self.logger.warning(f"No se encontró archivo de marcas para {entrevista_id}")
        except Exception as e:
            self.logger.error(f"Error cargando marca para {fragmento['name']}: {e}")

        marca_info = f"""
        ⏰ <b>Inicio original:</b> {marca_inicio}s<br>
        ⏹️ <b>Fin original:</b> {marca_fin}s<br>
        📝 <b>Nota:</b> {marca_nota}
        """
        self.marca_info.setText(marca_info)

    def proceder_analisis(self):
        """Proceder al análisis de emociones con los fragmentos seleccionados"""
        if not self.current_entrevista or not self.fragmentos_data:
            self.mostrar_error("No hay fragmentos seleccionados para analizar")
            return

        # Aquí puedes implementar la lógica para pasar a la siguiente pantalla de análisis
        fragmentos_count = len(self.fragmentos_data)
        total_duracion = sum(self.obtener_duracion_segundos(frag) for frag in self.fragmentos_data)
        
        QMessageBox.information(
            self,
            "Listo para Análisis",
            f"✅ <b>Preparado para analizar:</b><br>"
            f"• {fragmentos_count} fragmentos<br>"
            f"• Duración total: {self.formatear_duracion(total_duracion)}<br>"
            f"• Entrevista: {self.current_entrevista}<br><br>"
            f"Proceda a la siguiente pantalla para el análisis de emociones.",
            QMessageBox.Ok
        )
        
        self.logger.info(f"Iniciando análisis para entrevista {self.current_entrevista} con {fragmentos_count} fragmentos")

    def formatear_duracion(self, seconds):
        """Formatear duración en segundos a formato legible"""
        if seconds == "N/A" or seconds == 0:
            return "N/A"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def formatear_tamaño_archivo(self, size_bytes):
        """Formatear tamaño de archivo a formato legible"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def mostrar_error(self, msg):
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Error")
        msgbox.setText(msg)
        msgbox.setIcon(QMessageBox.Critical)
        msgbox.setStyleSheet("""
            QLabel { 
                color: #000000; 
                background-color: white; 
            }
        """)
        msgbox.exec()
        self.logger.error(msg)

    def mostrar_info(self, msg):
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Información")
        msgbox.setText(msg)
        msgbox.setIcon(QMessageBox.Information)
        msgbox.setStyleSheet("""
            QLabel { 
                color: #000000; 
                background-color: white; 
            }
        """)
        msgbox.exec()
        self.logger.info(msg)