import logging
import os
import json
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QFrame,
    QTextEdit, QSplitter, QMessageBox, QProgressBar,
    QComboBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor
import cv2
import traceback

# Importar clase de análisis
from classes.analisis import Analisis


class AnalysisThread(QThread):
    """Hilo de fondo para generar análisis sin congelar la UI"""
    progress_updated = Signal(int)
    log_message = Signal(str)
    finished_with_success = Signal(int, int)
    error_occurred = Signal(str)

    def __init__(self, fragmentos_data, modelo_path, resultados_dir):
        super().__init__()
        self.fragmentos_data = fragmentos_data
        self.modelo_path = modelo_path
        self.resultados_dir = resultados_dir
        self.logger = logging.getLogger(__name__)

    def run(self):
        try:
            total = len(self.fragmentos_data)
            exitos = 0

            if total == 0:
                self.log_message.emit("⚠️ No hay fragmentos válidos para analizar.")
                self.finished_with_success.emit(0, 0)
                return

            # Inicializar el analizador
            try:
                analizador = Analisis(self.modelo_path)
                self.log_message.emit(f"✅ Modelo cargado: {self.modelo_path.name}")
            except Exception as e:
                self.error_occurred.emit(f"❌ Error al cargar el modelo: {str(e)}")
                return

            for idx, fragmento in enumerate(self.fragmentos_data, 1):
                try:
                    fragmento_path = fragmento['path']
                    fragmento_name = fragmento['name']
                    
                    self.log_message.emit(f"🔍 Analizando: {fragmento_name}")
                    
                    # Realizar análisis del fragmento
                    resultados = analizador.analizar_fragmento(fragmento_path)
                    
                    if resultados:
                        # Generar resumen
                        resumen = analizador.get_emotion_summary(resultados)
                        
                        # Guardar resultados
                        self.guardar_resultados(fragmento, resumen, resultados)
                        
                        msg = f"✅ Análisis completado: {fragmento_name}"
                        self.log_message.emit(msg)
                        self.logger.info(msg)
                        exitos += 1
                    else:
                        msg = f"⚠️ No se detectaron rostros en: {fragmento_name}"
                        self.log_message.emit(msg)
                        self.logger.warning(msg)

                except Exception as e:
                    error_msg = f"❌ Error analizando {fragmento.get('name', 'fragmento')}: {str(e)}"
                    self.log_message.emit(error_msg)
                    self.logger.error(error_msg)
                    self.logger.debug(traceback.format_exc())

                # Emitir progreso
                self.progress_updated.emit(int((idx / total) * 100))

            self.progress_updated.emit(100)
            self.finished_with_success.emit(exitos, total)
            self.log_message.emit(f"🏁 Proceso finalizado ({exitos}/{total})")

        except Exception as e:
            error_msg = f"🔥 Error crítico en hilo de análisis: {str(e)}"
            self.logger.critical(error_msg)
            self.logger.debug(traceback.format_exc())
            self.error_occurred.emit(error_msg)

    def guardar_resultados(self, fragmento, resumen, resultados_detallados):
        """Guardar resultados del análisis en archivo JSON"""
        try:
            # Crear nombre de archivo para resultados
            resultado_file = self.resultados_dir / f"resultados_{fragmento['name'].replace('.mp4', '.json')}"
            
            datos_resultado = {
                'fragmento': {
                    'nombre': fragmento['name'],
                    'ruta': str(fragmento['path']),
                    'entrevista_id': fragmento.get('entrevista_id', 'N/A'),
                    'pregunta_id': fragmento.get('pregunta_id', 'N/A')
                },
                'analisis': {
                    'modelo_utilizado': self.modelo_path.name,
                    'fecha_analisis': datetime.now().isoformat(),
                    'total_frames_analizados': len(resultados_detallados),
                    'resumen_emociones': resumen,
                    'resultados_detallados': resultados_detallados
                }
            }
            
            with open(resultado_file, 'w', encoding='utf-8') as f:
                json.dump(datos_resultado, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Resultados guardados: {resultado_file.name}")
            
        except Exception as e:
            self.logger.error(f"Error guardando resultados: {str(e)}")
            raise


class AnalisisGenerarScreen(QWidget):
    """Pantalla para generar análisis de emociones desde fragmentos"""
    def __init__(self, logger=None, data_context=None, parent=None):
        super().__init__(parent)
        self.logger = logger or logging.getLogger(__name__)
        self.parent_window = parent
        self.fragmentos_data = []
        self.data_context = data_context or {"entrevistas": [], "fragmentos": []}
        self.current_entrevista = None
        self.modelos_disponibles = []
        self.modelo_seleccionado = None
        self.setup_ui()
        self.cargar_modelos()
        self.cargar_entrevistas()
        # Verificar estructura de directorios
        self.verificar_estructura_directorios()
        
    def cargar_modelos(self):
        """Cargar modelos disponibles desde la carpeta ml/"""
        try:
            ml_path = Path("ml")
            if not ml_path.exists():
                self.mostrar_error("No se encuentra la carpeta 'ml/' con los modelos")
                return

            modelos = list(ml_path.glob("*.h5")) + list(ml_path.glob("*.keras")) + list(ml_path.glob("*.model"))
            
            if len(modelos) == 0:
                self.mostrar_error("❌ No se encontraron modelos en la carpeta ml/")
                self.modelo_info_label.setText("❌ No hay modelos disponibles")
                return
                
            self.modelos_disponibles = modelos
            self.modelo_combo.clear()
            self.modelo_combo.addItem("-- Seleccione un modelo --")
            
            for modelo in modelos:
                # Verificar tamaño del modelo
                size_mb = modelo.stat().st_size / (1024 * 1024)
                self.modelo_combo.addItem(f"{modelo.name} ({size_mb:.1f} MB)")
            
            self.modelo_info_label.setText(f"✅ {len(modelos)} modelos disponibles")

        except Exception as e:
            self.mostrar_error(f"Error al cargar modelos: {str(e)}")

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

        left_panel = self.create_entrevistas_list_panel()
        right_panel = self.create_analysis_panel()

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
            QLabel {
                color: #000000;
            }
        """)
        layout = QVBoxLayout(frame)
        title = QLabel("🧠 Generador de Análisis de Emociones")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        desc = QLabel("Analice automáticamente las emociones en fragmentos de entrevistas usando modelos de IA")
        desc.setFont(QFont("Segoe UI", 12))
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)

        return frame

    # ------------------------------------------------------------------
    # Panel Izquierdo - Lista de Entrevistas y Fragmentos
    # ------------------------------------------------------------------
    def create_entrevistas_list_panel(self):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                border: 2px solid #c8e6c9;
            }
            QLabel {
                color: #000000;
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("📁 Entrevistas con Fragmentos")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(header)

        # Toolbar
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
        btn_refresh.clicked.connect(self.cargar_entrevistas)

        self.status_label = QLabel("Cargando entrevistas...")
        self.status_label.setStyleSheet("color: #000000; font-style: italic;")
        toolbar.addWidget(btn_refresh)
        toolbar.addWidget(self.status_label)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # ComboBox para entrevistas
        entrevista_layout = QHBoxLayout()
        entrevista_label = QLabel("Seleccionar Entrevista:")
        entrevista_label.setStyleSheet("color: #000000; font-weight: bold;")
        self.entrevista_combo = QComboBox()
        self.entrevista_combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: 2px solid #4caf50;
                border-radius: 8px;
                padding: 8px 12px;
                color: #000000;
            }
        """)
        self.entrevista_combo.currentTextChanged.connect(self.on_entrevista_selected)
        entrevista_layout.addWidget(entrevista_label)
        entrevista_layout.addWidget(self.entrevista_combo)
        entrevista_layout.addStretch()
        layout.addLayout(entrevista_layout)

        # Tabla de fragmentos
        self.fragmentos_table = QTableWidget()
        self.fragmentos_table.setColumnCount(4)
        self.fragmentos_table.setHorizontalHeaderLabels([
            "🎬 Fragmento", "⏱️ Duración", "📊 Tamaño", "📅 Creación"
        ])
        self.fragmentos_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 4):
            self.fragmentos_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)

        self.fragmentos_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.fragmentos_table.setAlternatingRowColors(True)
        self.fragmentos_table.setStyleSheet("""
            QTableWidget { 
                background-color: white; 
                alternate-background-color: #f5f5f5; 
                gridline-color: #e0e0e0; 
                color: #000000;
            }
            QTableWidget::item { 
                color: #000000; 
                padding: 5px; 
            }
            QHeaderView::section { 
                color: #000000; 
                background-color: #e8f5e8; 
                padding: 5px; 
                border: 1px solid #c8e6c9; 
            }
        """)
        layout.addWidget(self.fragmentos_table)

        return frame

    # ------------------------------------------------------------------
    # Panel Derecho - Configuración de Análisis
    # ------------------------------------------------------------------
    def create_analysis_panel(self):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                border: 2px solid #c8e6c9;
            }
            QLabel {
                color: #000000;
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("⚙️ Configuración de Análisis")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(header)

        # Información de la entrevista seleccionada
        self.entrevista_info_label = QLabel("Seleccione una entrevista para ver los fragmentos disponibles.")
        self.entrevista_info_label.setWordWrap(True)
        layout.addWidget(self.entrevista_info_label)

        # Selección de modelo
        modelo_layout = QHBoxLayout()
        modelo_label = QLabel("🤖 Modelo de IA:")
        modelo_label.setStyleSheet("font-weight: bold;")
        self.modelo_combo = QComboBox()
        self.modelo_combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: 2px solid #4caf50;
                border-radius: 8px;
                padding: 8px 12px;
                color: #000000;
            }
        """)
        self.modelo_combo.currentTextChanged.connect(self.on_modelo_selected)
        modelo_layout.addWidget(modelo_label)
        modelo_layout.addWidget(self.modelo_combo)
        modelo_layout.addStretch()
        layout.addLayout(modelo_layout)

        # Información del modelo seleccionado
        self.modelo_info_label = QLabel("Seleccione un modelo de la lista")
        self.modelo_info_label.setStyleSheet("color: #666666; font-style: italic;")
        layout.addWidget(self.modelo_info_label)

        # Estadísticas de fragmentos
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background: #f1f8e9;
                border-radius: 10px;
                border: 1px solid #c8e6c9;
                padding: 15px;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        stats_header = QLabel("📈 Estadísticas de Fragmentos")
        stats_header.setStyleSheet("font-weight: bold;")
        stats_layout.addWidget(stats_header)
        self.stats_label = QLabel("No hay fragmentos seleccionados")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)
        layout.addWidget(stats_frame)
        
        buttons_layout = QHBoxLayout()

        # Botón generar análisis
        self.btn_analizar = QPushButton("🧠 Generar Análisis de Emociones")
        self.btn_analizar.setEnabled(False)
        self.btn_analizar.clicked.connect(self.generar_analisis)
        self.btn_analizar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4caf50, stop:1 #388e3c);
                color: white; border-radius: 12px;
                padding: 12px 24px; font-weight: bold;
                font-size: 14px;
            }
            QPushButton:disabled { 
                background: #9e9e9e; 
                color: #cccccc; 
            }
            QPushButton:hover:enabled { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5cb860, stop:1 #4caf50);
            }
        """)

        #boton cancelar 
        self.btn_cancelar = QPushButton("❌ Cancelar Análisis")
        self.btn_cancelar.setEnabled(False)
        self.btn_cancelar.clicked.connect(self.cancelar_analisis)
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background: #e53935; color: white; border-radius: 12px;
                padding: 12px 24px; font-weight: bold; font-size: 14px;
            }
            QPushButton:disabled { background: #9e9e9e; color: #cccccc; }
            QPushButton:hover:enabled { background: #d32f2f; }
        """)
        
        buttons_layout.addWidget(self.btn_analizar)
        buttons_layout.addWidget(self.btn_cancelar)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
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
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #c8e6c9;
                border-radius: 5px;
                text-align: center;
                color: #000000;
            }
            QProgressBar::chunk {
                background-color: #4caf50;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress)
        return frame

    def create_log_frame(self):
        frame = QFrame()
        layout = QVBoxLayout(frame)
        label = QLabel("📝 Registro del Proceso de Análisis")
        label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        label.setStyleSheet("color: #000000;")
        layout.addWidget(label)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("color: #000000; background-color: white;")
        layout.addWidget(self.log_output)
        return frame


    
    def cancelar_analisis(self):
        if hasattr(self, 'thread') and self.thread and self.thread.isRunning():
            self.thread.terminate()  # Termina el hilo
            self.thread.wait()
            self.log_output.append("❌ Análisis cancelado por el usuario.")
            self.btn_analizar.setEnabled(True)
            self.btn_cancelar.setEnabled(False)
            
    # ------------------------------------------------------------------
    # Lógica de Carga de Datos
    # ------------------------------------------------------------------
    def cargar_modelos(self):
        """Cargar modelos disponibles desde la carpeta ml/"""
        try:
            ml_path = Path("ml")
            if not ml_path.exists():
                self.mostrar_error("No se encuentra la carpeta 'ml/' con los modelos")
                return

            # Buscar archivos de modelo (ajusta las extensiones según tus modelos)
            modelos = list(ml_path.glob("*.h5")) + list(ml_path.glob("*.keras")) + list(ml_path.glob("*.model"))
            
            self.modelos_disponibles = modelos
            self.modelo_combo.clear()
            self.modelo_combo.addItem("-- Seleccione un modelo --")
            
            for modelo in modelos:
                self.modelo_combo.addItem(modelo.name)
            
            if len(modelos) == 0:
                self.modelo_info_label.setText("❌ No se encontraron modelos en la carpeta ml/")
            else:
                self.modelo_info_label.setText(f"✅ {len(modelos)} modelos disponibles")

        except Exception as e:
            self.mostrar_error(f"Error al cargar modelos: {str(e)}")

    def cargar_entrevistas(self):
        """Cargar lista de entrevistas con fragmentos disponibles"""
        try:
            self.status_label.setText("Buscando entrevistas...")
            fragmentos_dir = Path("data/fragmentos")
            if not fragmentos_dir.exists():
                self.mostrar_error("No se encuentra el directorio de fragmentos")
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
                self.status_label.setText("ℹ️ No hay entrevistas con fragmentos generados")
            else:
                self.status_label.setText(f"✅ {len(entrevistas)} entrevistas con fragmentos encontradas")

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

        # Extraer ID de entrevista del texto
        entrevista_id = texto.split(' ')[0]
        self.current_entrevista = entrevista_id
        self.cargar_fragmentos_entrevista(entrevista_id)

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
                        'creation_time': datetime.fromtimestamp(stat.st_ctime)
                    }
                    
                    # Extraer información adicional del nombre del archivo
                    self.extraer_info_fragmento(fragmento_info, frag_path.name)
                    
                    self.fragmentos_data.append(fragmento_info)
                    
                except Exception as e:
                    self.logger.error(f"Error procesando {frag_path}: {str(e)}")
                    continue

            self.actualizar_tabla_fragmentos()
            self.actualizar_estadisticas()
            self.actualizar_boton_analizar()

        except Exception as e:
            self.mostrar_error(f"Error al cargar fragmentos: {str(e)}")

    def extraer_info_fragmento(self, fragmento_info, filename):
        """Extraer información de la entrevista y pregunta desde el nombre del archivo"""
        try:
            name = filename.replace(".mp4", "")
            parts = name.split("_")
            
            if len(parts) >= 3:
                fragmento_info["entrevista_id"] = "_".join(parts[1:-1])
                fragmento_info["pregunta_id"] = parts[-1]
            else:
                fragmento_info["entrevista_id"] = "N/A"
                fragmento_info["pregunta_id"] = "N/A"
                
        except Exception as e:
            self.logger.warning(f"Error extrayendo info de {filename}: {e}")
            fragmento_info["entrevista_id"] = "N/A"
            fragmento_info["pregunta_id"] = "N/A"

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
        """Actualizar la tabla con los fragmentos cargados y agregar checkboxes"""
        # Configurar columnas para incluir checkbox
        self.fragmentos_table.setColumnCount(5)
        self.fragmentos_table.setHorizontalHeaderLabels([
            "✅", "🎬 Fragmento", "⏱️ Duración", "📊 Tamaño", "📅 Creación"
        ])
        
        # Configurar headers
        self.fragmentos_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Checkbox
        self.fragmentos_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Nombre
        self.fragmentos_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Duración
        self.fragmentos_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Tamaño
        self.fragmentos_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Fecha
        
        self.fragmentos_table.setRowCount(len(self.fragmentos_data))
        
        for row, frag in enumerate(self.fragmentos_data):
            # Checkbox (columna 0)
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            checkbox_item.setCheckState(Qt.Checked)  # Por defecto seleccionado
            self.fragmentos_table.setItem(row, 0, checkbox_item)
            
            # Nombre del fragmento (columna 1)
            name_item = QTableWidgetItem(frag['name'])
            name_item.setData(Qt.UserRole, row)
            self.fragmentos_table.setItem(row, 1, name_item)
            
            # Duración (columna 2)
            duration_item = QTableWidgetItem(frag['duration'])
            self.fragmentos_table.setItem(row, 2, duration_item)
            
            # Tamaño (columna 3)
            size_item = QTableWidgetItem(self.formatear_tamaño_archivo(frag['size']))
            self.fragmentos_table.setItem(row, 3, size_item)
            
            # Fecha de creación (columna 4)
            date_item = QTableWidgetItem(frag['creation_time'].strftime("%Y-%m-%d %H:%M"))
            self.fragmentos_table.setItem(row, 4, date_item)

    def actualizar_estadisticas(self):
        """Actualizar las estadísticas de la entrevista seleccionada"""
        if not self.current_entrevista or not self.fragmentos_data:
            self.entrevista_info_label.setText("Seleccione una entrevista para ver los fragmentos disponibles.")
            self.stats_label.setText("No hay fragmentos seleccionados")
            return

        total_fragmentos = len(self.fragmentos_data)
        total_duracion = sum(self.obtener_duracion_segundos(frag) for frag in self.fragmentos_data)
        total_tamaño = sum(frag['size'] for frag in self.fragmentos_data)
        
        self.entrevista_info_label.setText(
            f"🎥 <b>Entrevista:</b> {self.current_entrevista}<br>"
            f"📁 <b>Fragmentos disponibles:</b> {total_fragmentos}<br>"
            f"⏱️ <b>Duración total:</b> {self.formatear_duracion(total_duracion)}<br>"
            f"📊 <b>Tamaño total:</b> {self.formatear_tamaño_archivo(total_tamaño)}"
        )
        
        stats_text = f"""
        • <b>Total de fragmentos:</b> {total_fragmentos}<br>
        • <b>Duración total:</b> {self.formatear_duracion(total_duracion)}<br>
        • <b>Tamaño total:</b> {self.formatear_tamaño_archivo(total_tamaño)}<br>
        • <b>Fragmento más largo:</b> {self.obtener_fragmento_mas_largo()}<br>
        • <b>Fragmento más corto:</b> {self.obtener_fragmento_mas_corto()}
        """
        
        self.stats_label.setText(stats_text)

    def verificar_estructura_directorios(self):
        """Verificar que la estructura de directorios necesaria existe"""
        directorios_necesarios = [
            Path("data/resultados"),
            Path("ml")
        ]
        
        for directorio in directorios_necesarios:
            if not directorio.exists():
                directorio.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Directorio creado: {directorio}")
                
    def actualizar_boton_analizar(self):
        """Actualizar estado del botón de análisis"""
        tiene_fragmentos = len(self.fragmentos_data) > 0
        tiene_modelo = self.modelo_seleccionado is not None
        self.btn_analizar.setEnabled(tiene_fragmentos and tiene_modelo)

    # ------------------------------------------------------------------
    # Selección de Modelo
    # ------------------------------------------------------------------
    def on_modelo_selected(self, texto):
        """Manejar selección de modelo"""
        if texto == "-- Seleccione un modelo --" or not texto:
            self.modelo_seleccionado = None
            self.modelo_info_label.setText("Seleccione un modelo de la lista")
            self.actualizar_boton_analizar()
            return

        # Encontrar el modelo seleccionado
        for modelo in self.modelos_disponibles:
            if modelo.name == texto:
                self.modelo_seleccionado = modelo
                self.modelo_info_label.setText(f"✅ Modelo seleccionado: {modelo.name}<br>📍 Ruta: {modelo}")
                self.actualizar_boton_analizar()
                break


    def get_fragmentos_seleccionados(self):
        """Obtener lista de fragmentos seleccionados por el usuario"""
        selected = []
        for row in range(self.fragmentos_table.rowCount()):
            checkbox_item = self.fragmentos_table.item(row, 0)  # Columna del checkbox
            if checkbox_item and checkbox_item.checkState() == Qt.Checked:
                # Obtener el índice del fragmento desde la columna del nombre
                name_item = self.fragmentos_table.item(row, 1)
                if name_item:
                    frag_index = name_item.data(Qt.UserRole)
                    if frag_index is not None and 0 <= frag_index < len(self.fragmentos_data):
                        selected.append(self.fragmentos_data[frag_index])
        return selected

    # ------------------------------------------------------------------
    # Generación de Análisis
    # ------------------------------------------------------------------
    def generar_analisis(self):
        selected_fragmentos = self.get_fragmentos_seleccionados()
        if not self.current_entrevista or not selected_fragmentos or not self.modelo_seleccionado:
            self.mostrar_advertencia("Seleccione una entrevista con fragmentos y un modelo válido.")
            return

        resultados_dir = Path(f"data/resultados/{self.current_entrevista}")
        resultados_dir.mkdir(parents=True, exist_ok=True)

        self.log_output.clear()
        self.log_output.append(f"🚀 Iniciando análisis de emociones para {self.current_entrevista}")
        self.log_output.append(f"🤖 Modelo: {self.modelo_seleccionado.name}")
        self.log_output.append(f"📁 Fragmentos a analizar: {len(selected_fragmentos)}")

        # Iniciar hilo de análisis
        self.thread = AnalysisThread(selected_fragmentos, self.modelo_seleccionado, resultados_dir)
        self.thread.progress_updated.connect(self.progress.setValue)
        self.thread.log_message.connect(self.log_output.append)
        self.thread.finished_with_success.connect(self.on_analysis_finished)
        self.thread.error_occurred.connect(self.on_analysis_error)
        self.thread.start()
        self.btn_analizar.setEnabled(False)
        self.btn_cancelar.setEnabled(True)


    def on_analysis_finished(self, exitos, total):
        """Manejar finalización exitosa del análisis"""
        msg_text = f"🏁 Análisis completado: {exitos}/{total} fragmentos procesados exitosamente."
        self.log_output.append(msg_text)
        self.logger.info(msg_text)
        self.btn_analizar.setEnabled(True)
        self.btn_cancelar.setEnabled(False)

        

        # Mantener referencia del hilo
        thread_ref = self.thread

        msgbox = QMessageBox(self)
        msgbox.setWindowTitle("Análisis Completado")
        msgbox.setText(msg_text)
        msgbox.setIcon(QMessageBox.Information)
        msgbox.setStyleSheet("QLabel { color: #000000; background-color: white; }")
        msgbox.exec()

        # Limpiar hilo
        if thread_ref:
            thread_ref.quit()
            thread_ref.wait()
            thread_ref.deleteLater()
            self.thread = None

    def on_analysis_error(self, msg_text):
        """Manejar error en el análisis"""
        self.log_output.append(f"❌ {msg_text}")
        self.logger.error(msg_text)
        self.btn_analizar.setEnabled(True)
        
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Error en Análisis")
        msgbox.setText(msg_text)
        msgbox.setIcon(QMessageBox.Critical)
        msgbox.setStyleSheet("QLabel { color: #000000; background-color: white; }")
        msgbox.exec()

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
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
        return f"{mas_largo['duration']}"

    def obtener_fragmento_mas_corto(self):
        """Obtener información del fragmento más corto"""
        if not self.fragmentos_data:
            return "N/A"
        
        fragmentos_validos = [f for f in self.fragmentos_data if self.obtener_duracion_segundos(f) > 0]
        if not fragmentos_validos:
            return "N/A"
        
        mas_corto = min(fragmentos_validos, key=lambda x: self.obtener_duracion_segundos(x))
        return f"{mas_corto['duration']}"

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

    def mostrar_error(self, msg):
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Error")
        msgbox.setText(msg)
        msgbox.setIcon(QMessageBox.Critical)
        msgbox.setStyleSheet("QLabel { color: #000000; background-color: white; }")
        msgbox.exec()
        self.logger.error(msg)

    def mostrar_advertencia(self, msg):
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Advertencia")
        msgbox.setText(msg)
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setStyleSheet("QLabel { color: #000000; background-color: white; }")
        msgbox.exec()
        self.logger.warning(msg)