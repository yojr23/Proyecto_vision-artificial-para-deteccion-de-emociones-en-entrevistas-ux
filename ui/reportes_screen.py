import logging
from pathlib import Path
import json
from datetime import datetime
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QMessageBox, QStackedWidget, QFrame, QScrollArea, QPushButton, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Importar componentes
from .utils.buttons import ModernButton
from .utils.footer import AnimatedFooter
from .utils.styles import (
    ColorPalette, GradientStyles, CommonStyles, 
    MessageBoxStyles, LayoutSettings, FontSettings
)

# Asumimos que crearás estas pantallas en reportes_screens/
# from .reportes_screens.resumen_screen import ResumenScreen
# from .reportes_screens.detalle_screen import DetalleScreen
# from .reportes_screens.export_screen import ExportScreen

# 🔹 Definir paleta de colores verde agrícola completa
AGRICULTURAL_GREEN_PALETTE = {
    'DARK_GREEN': '#1b5e20',
    'PRIMARY_GREEN': '#2e7d32', 
    'MEDIUM_GREEN': '#388e3c',
    'LIGHT_GREEN': '#4caf50',
    'SOFT_GREEN': '#66bb6a',
    'BRIGHT_GREEN': '#81c784',
    'PALE_GREEN': '#a5d6a7',
    'MINT_GREEN': '#c8e6c9',
    'WHITE_GREEN': '#e8f5e9',
    'FOREST_GREEN': '#2e572c',
    'SPRING_GREEN': '#43a047',
    'GRASS_GREEN': '#558b2f',
    'LEAF_GREEN': '#689f38'
}


class ReportesMainWindow(QMainWindow):
    def __init__(self, parent=None, logger=None):
        super().__init__(parent)
        self.logger = logger or logging.getLogger(__name__)
        self.setWindowTitle("Módulo de Reportes - AGRIOT")
        self.resize(1400, 800)
        self.current_entrevista_id = None  # Para trackear la entrevista seleccionada

        # Aplicar gradiente verde de fondo global
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {ColorPalette.DARK_GREEN}, 
                    stop:0.3 {ColorPalette.PRIMARY_GREEN},
                    stop:0.7 {ColorPalette.LIGHT_GREEN},
                    stop:1 {ColorPalette.SOFT_GREEN});
                color: black;  /* Texto negro por defecto en toda la ventana */
            }}
            QLabel {{
                color: black;  /* Asegurar texto negro en labels */
            }}
            QStackedWidget {{
                background: transparent;
                border: none;
            }}
        """)

        self._check_directories()
        self.data_context = {}  # Se cargará en setup_ui
        self.setup_ui()
        self.load_reportes_data()  # Cargar al init
        self.populate_entrevista_selector()  # Poblar después de cargar datos

    def populate_entrevista_selector(self):
        """Poblar el selector de entrevistas con datos ordenados."""
        self.entrevista_selector.clear()  # Limpiar si hay items previos
        for ent in self.data_context.get("entrevistas", []):
            self.entrevista_selector.addItem(ent["nombre"])

    def load_reportes_data(self):
        """Cargar datos globales de entrevistas, puntajes emocionales y marcas (comentarios/notas)."""
        try:
            data = {
                "entrevistas": [],  # Lista de dicts con info general por entrevista
                "por_entrevista": {},  # {id_entrevista: {pregunta_id: {emociones, intensidad, nota, inicio, fin, video_full}, ...}}
                "videos": []  # Full videos de entrevistas
            }
            marcas_path = Path("data/marcas")  # JSONs como marcas_2025-10-05_005.json
            puntajes_path = Path("data/puntajes")  # JSONs como puntajes_2025-10-05_005.json con {"pregunta_1": {...}, ...}
            videos_path = Path("data/videos_originales")

            # 🔹 Recorrer archivos de marcas para obtener entrevistas y comentarios/notas
            for marcas_file in marcas_path.glob("marcas_*.json"):
                entrevista_id = marcas_file.stem.replace("marcas_", "")
                with open(marcas_file, "r", encoding="utf-8") as f:
                    marcas_data = json.load(f)

                # Cargar puntajes correspondientes para emociones
                puntajes_file = puntajes_path / f"puntajes_{entrevista_id}.json"
                if not puntajes_file.exists():
                    self.logger.warning(f"No se encontró puntajes para {entrevista_id}")
                    continue
                with open(puntajes_file, "r", encoding="utf-8") as pf:
                    emociones_data = json.load(pf)  # {"pregunta_1": {"emociones_detectadas": [...], "intensidad": {...}}, ...}

                # Info general de la entrevista
                marcas_list = marcas_data.get("marcas", [])
                info = {
                    "id": entrevista_id,
                    "nombre": f"Entrevista {entrevista_id}",
                    "num_preguntas": len(marcas_list),
                    "promedios_globales": self._calcular_promedios_globales(emociones_data),  # Función helper
                    "fecha": datetime.fromtimestamp(marcas_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                    "video_full": marcas_data.get("archivo_video", "")
                }
                data["entrevistas"].append(info)

                # Detalle por pregunta (usando pregunta_id como key, ej: 1 -> "pregunta_1")
                por_pregunta = {}
                for marca in marcas_list:
                    pregunta_id = marca["pregunta_id"]
                    pregunta_key = f"pregunta_{pregunta_id}"  # Asumir key en puntajes como "pregunta_1"
                    info_preg = emociones_data.get(pregunta_key, {})
                    
                    por_pregunta[str(pregunta_id)] = {  # Key como str(pregunta_id) para consistencia
                        "emociones_detectadas": info_preg.get("emociones_detectadas", []),
                        "intensidad": info_preg.get("intensidad", {}),
                        "nota": marca.get("nota", ""),  # Comentario del entrevistador
                        "inicio": marca.get("inicio", 0),
                        "fin": marca.get("fin", 0),
                        "video_full": info["video_full"]  # Full video path, player seekeará a inicio/fin
                    }
                data["por_entrevista"][entrevista_id] = por_pregunta

            # Cargar videos full (ya referenciados en marcas, pero para lista general)
            for video_file in videos_path.glob("*.mp4"):
                info = {
                    "nombre": video_file.name,
                    "ruta": str(video_file),
                    "tamano": video_file.stat().st_size,
                    "fecha": datetime.fromtimestamp(video_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                }
                data["videos"].append(info)

            # Ordenar entrevistas de la más nueva a la más antigua por fecha
            data["entrevistas"].sort(key=lambda x: datetime.strptime(x["fecha"], "%Y-%m-%d %H:%M"), reverse=True)

            self.data_context = data
            self.logger.info(f"Datos de reportes cargados: {len(data['entrevistas'])} entrevistas.")
            return True

        except Exception as e:
            self.logger.error(f"Error cargando datos de reportes: {str(e)}")
            self.data_context = {"entrevistas": [], "por_entrevista": {}, "videos": []}
            return False

    def _calcular_promedios_globales(self, emociones_data):
        """Helper: Calcula promedios de intensidades para las 7 emociones."""
        emociones = ["ira", "disgusto", "miedo", "felicidad", "sorpresa", "tristeza", "neutral"]
        totales = {emo: 0 for emo in emociones}
        count = 0
        for info_preg in emociones_data.values():
            intens = info_preg.get("intensidad", {})
            for emo in emociones:
                totales[emo] += intens.get(emo, 0)
            count += 1
        if count == 0:
            return {emo: 0 for emo in emociones}
        return {emo: totales[emo] / count for emo in emociones}

    # ------------------------------------------------------------------
    # 🔹 Verificar carpetas
    # ------------------------------------------------------------------
    def _check_directories(self):
        self.Videos_path = Path("data/videos_originales")
        self.Marcas_path = Path("data/marcas")
        self.Puntajes_path = Path("data/puntajes")

        for path in [self.Videos_path, self.Marcas_path, self.Puntajes_path]:
            if not path.is_dir():
                raise ValueError(f"El directorio {path} no existe o no es válido")
   
    def setup_ui(self):
        """Construir la interfaz con scroll vertical"""
        # ----- Contenedor principal con scroll -----
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(240,255,240,0.6);
                width: 14px;
                margin: 10px 0 10px 0;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: rgba(76,175,80,0.8);
                min-height: 25px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(56,142,60,0.9);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # ----- Contenedor interno -----
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)

        # Layout principal dentro del scroll
        main_layout = QVBoxLayout(scroll_content)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(40, 20, 40, 15)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 🔸 Header con diseño de campo mejorado
        header_frame = self.create_header_frame()
        main_layout.addWidget(header_frame)
        
        # 🔸 Menú inferior
        menu_frame = self.create_menu_frame()
        main_layout.addWidget(menu_frame)

        # 🔸 Stack de pantallas con diseño de invernadero
        stack_frame = QFrame()
        stack_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 rgba(255, 255, 255, 0.95), 
                    stop:0.5 rgba(248, 255, 248, 0.92),
                    stop:1 rgba(240, 255, 240, 0.95));
                border-radius: 25px;
                border: 3px solid {ColorPalette.LIGHT_GREEN};
                box-shadow: 0 8px 32px rgba(34, 139, 34, 0.3);
                color: black;  /* Texto negro explícito en stack */
            }}
        """)
        stack_layout = QVBoxLayout(stack_frame)
        stack_layout.setContentsMargins(25, 25, 25, 25)
        self.stack = QStackedWidget()
        stack_layout.addWidget(self.stack)
        main_layout.addWidget(stack_frame, stretch=1)
        
        # Agregar subpantallas al stack (descomenta cuando crees las clases)
        # self.resumen_screen = ResumenScreen(logger=self.logger, data_context=self.data_context, parent=self)
        # self.detalle_screen = DetalleScreen(logger=self.logger, data_context=self.data_context, parent=self)
        # self.export_screen = ExportScreen(logger=self.logger, data_context=self.data_context, parent=self)
        # self.stack.addWidget(self.resumen_screen)
        # self.stack.addWidget(self.detalle_screen)
        # self.stack.addWidget(self.export_screen)
        # self.stack.setCurrentWidget(self.resumen_screen)  # Default a resumen

        # Placeholder si no hay datos
        if not self.data_context.get("entrevistas"):
            no_data_label = QLabel("🌱 No hay reportes disponibles. Analiza una entrevista primero.")
            no_data_label.setFont(QFont("Arial", 14, QFont.Weight.Medium))
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("""
                QLabel {
                    color: black;  /* Texto negro explícito */
                    padding: 30px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(255, 255, 255, 0.9),
                        stop:1 rgba(240, 255, 240, 0.9));
                    border-radius: 20px;
                    border: 2px dashed #7cb342;
                    margin: 20px;
                }
            """)
            stack_layout.addWidget(no_data_label)

        # 🔸 Footer
        footer = AnimatedFooter(100)
        main_layout.addWidget(footer)

        # Asignar scroll como contenido central
        central_widget = QWidget()
        layout_container = QVBoxLayout(central_widget)
        layout_container.addWidget(scroll_area)
        self.setCentralWidget(central_widget)

    def create_header_frame(self):
        """Crear el encabezado superior con diseño agrícola"""
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(46, 125, 50, 0.85),
                    stop:0.3 rgba(56, 142, 60, 0.8),
                    stop:0.6 rgba(76, 175, 80, 0.75),
                    stop:1 rgba(105, 240, 174, 0.7));
                border-radius: 30px;
                border: 3px solid rgba(255, 255, 255, 0.3);
                padding: 25px;
                box-shadow: 0 6px 25px rgba(34, 139, 34, 0.4);
                color: black;  /* Texto negro explícito en header (aunque overrides para títulos) */
            }}
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(12)
        header_layout.setContentsMargins(30, 20, 30, 20)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icono decorativo superior
        icon_label = QLabel("📊🌾📈")
        icon_label.setFont(QFont("Arial", 24))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                color: #ffffff;  /* Mantener blanco para icono en fondo oscuro */
                background: transparent;
                padding: 5px;
            }
        """)
        header_layout.addWidget(icon_label)

        # Título principal con efecto de texto agrícola
        title = QLabel("Dashboard de Reportes Emocionales")
        title.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #ffffff;  /* Blanco para título en header oscuro */
                background: transparent;
                padding: 15px 30px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                letter-spacing: 1.5px;
                border-bottom: 3px solid rgba(255, 255, 255, 0.5);
            }
        """)
        header_layout.addWidget(title)

        # Selector de entrevista (QComboBox)
        selector_layout = QHBoxLayout()
        selector_label = QLabel("Seleccionar Entrevista:")
        selector_label.setStyleSheet("color: #000000; font-size: 14px; padding-right: 10px;") 
        self.entrevista_selector = QComboBox()  # Crear primero
        self.entrevista_selector.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 0.9);
                border: 2px solid #4caf50;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
                min-width: 200px;
                color: black;  /* Texto negro explícito en combo */
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                color: black;  /* Negro en el dropdown */
                background: white;
                selection-background-color: #4caf50;
                selection-color: white;
            }
        """)
        # Poblar después de cargar data en load_reportes_data, vía signal o manual
        self.entrevista_selector.currentTextChanged.connect(self.on_entrevista_selected)
        selector_layout.addWidget(selector_label)
        selector_layout.addWidget(self.entrevista_selector)
        selector_layout.addStretch()
        header_layout.addLayout(selector_layout)

        # Subtítulo con diseño orgánico
        subtitle = QLabel("Visualiza emociones en entrevistas: radares globales y por pregunta para insights profundos")
        subtitle.setFont(QFont("Segoe UI", 16, QFont.Weight.Medium))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: #e8f5e9;  /* Mantener claro para subtítulo */
                background: rgba(255, 255, 255, 0.15);
                padding: 12px 25px;
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                margin: 10px 50px;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
            }
        """)
        header_layout.addWidget(subtitle)

        return header_frame

    def on_entrevista_selected(self, text):
        """Maneja cambio de entrevista seleccionada."""
        if text:
            self.current_entrevista_id = text.split()[-1]  # Extrae ID como "Entrevista 2025-10-05_005" -> "2025-10-05_005"
            # Actualiza sub-screens: self.resumen_screen.update_data(self.data_context, self.current_entrevista_id)
            self.logger.info(f"Entrevista seleccionada: {self.current_entrevista_id}")

    def create_menu_frame(self):
        """Crear frame para menú inferior con diseño de huerto moderno"""
        menu_frame = QFrame()
        menu_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 255, 255, 0.9),
                    stop:0.5 rgba(240, 255, 240, 0.85),
                    stop:1 rgba(232, 245, 233, 0.9));
                border-radius: 25px;
                border: 3px solid {ColorPalette.LIGHT_GREEN};
                padding: 25px;
                box-shadow: 0 5px 20px rgba(34, 139, 34, 0.25);
                color: black;  /* Texto negro explícito en menú */
            }}
        """)
        menu_layout = QHBoxLayout(menu_frame)
        menu_layout.setAlignment(Qt.AlignCenter)
        menu_layout.setSpacing(25)

        # Botones adaptados para reportes
        btn_resumen = ModernButton("📊 Resumen Global", button_type="primary")
        btn_detalle = ModernButton("🔍 Detalle por Pregunta", button_type="secondary")
        btn_export = ModernButton("📤 Exportar Reporte", button_type="secondary")
        btn_volver = ModernButton("🏠 Volver al Menú", button_type="accent")

        # Estilos (reutiliza los del fragmento, con negro explícito)
        button_styles = """
            QPushButton {
                color: black;  /* Texto negro explícito */
                font-weight: 600;
                font-size: 14px;
                border-radius: 15px;
                padding: 14px 28px;
                min-width: 200px;
                min-height: 50px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.9),
                    stop:1 rgba(240, 255, 240, 0.8));
                border: 2px solid #7cb342;
                box-shadow: 0 4px 15px rgba(124, 179, 66, 0.2);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(232, 245, 233, 0.95),
                    stop:1 rgba(220, 240, 220, 0.9));
                border: 2px solid #4caf50;
                color: black;  /* Negro en hover */
                box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(200, 230, 201, 0.95),
                    stop:1 rgba(180, 220, 180, 0.9));
                color: black;  /* Negro en pressed */
            }
        """

        primary_button_style = """
            QPushButton {
                color: white;  /* Blanco para primario por contraste */
                font-weight: 700;
                font-size: 15px;
                border-radius: 15px;
                padding: 16px 30px;
                min-width: 220px;
                min-height: 55px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4caf50,
                    stop:0.3 #45a049,
                    stop:0.7 #3d8b40,
                    stop:1 #357a38);
                border: 2px solid #2e7d32;
                box-shadow: 0 5px 18px rgba(76, 175, 80, 0.5);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5cb860,
                    stop:0.3 #54ae58,
                    stop:0.7 #4c9c50,
                    stop:1 #448b48);
                border: 2px solid #388e3c;
                color: white;  /* Blanco en hover primario */
                box-shadow: 0 7px 22px rgba(92, 184, 96, 0.6);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d8b40,
                    stop:0.3 #378035,
                    stop:0.7 #317534,
                    stop:1 #2b662e);
                color: white;  /* Blanco en pressed primario */
            }
        """

        # Aplicar estilos
        btn_resumen.setStyleSheet(primary_button_style)
        btn_detalle.setStyleSheet(button_styles)
        btn_export.setStyleSheet(button_styles)
        btn_volver.setStyleSheet(button_styles)

        # Conectar botones (descomenta cuando tengas screens)
        # btn_resumen.clicked.connect(lambda: self.stack.setCurrentWidget(self.resumen_screen))
        # btn_detalle.clicked.connect(lambda: self.stack.setCurrentWidget(self.detalle_screen))
        # btn_export.clicked.connect(lambda: self.stack.setCurrentWidget(self.export_screen) or self.exportar_reporte())
        btn_volver.clicked.connect(self.volver_menu_principal)

        # Agregar botones al layout
        for btn in [btn_resumen, btn_detalle, btn_export, btn_volver]:
            menu_layout.addWidget(btn)

        # Removido el poblar aquí; se hace en populate_entrevista_selector()

        return menu_frame

    def exportar_reporte(self):
        """Genera export del reporte actual (imgs de radares + ZIP/PDF). Implementa según necesites."""
        if not self.current_entrevista_id:
            self.show_warning("Selecciona una entrevista primero.")
            return
        # Lógica: usa matplotlib para savefig de radares, zipfile para paquete
        self.logger.info(f"Exportando reporte para {self.current_entrevista_id}")
        self.show_info("Reporte exportado exitosamente.")

    # ------------------------------------------------------------------
    # Utilidades (de tu código original)
    # ------------------------------------------------------------------
    def show_error(self, msg):
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Error")
        msgbox.setText(msg)
        msgbox.setIcon(QMessageBox.Critical)
        msgbox.setStyleSheet("""
            QLabel { 
                color: black;  /* Negro explícito en mensajes */
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
                color: black;  /* Negro explícito */
                background-color: white; 
            }
        """)
        msgbox.exec()
        self.logger.warning(msg)

    def show_info(self, msg):
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Información")
        msgbox.setText(msg)
        msgbox.setIcon(QMessageBox.Information)
        msgbox.setStyleSheet("""
            QLabel { 
                color: black;  /* Negro explícito */
                background-color: white; 
            }
        """)
        msgbox.exec()
        self.logger.info(msg)

    # ------------------------------------------------------------------
    # 🔹 Volver al menú principal
    # ------------------------------------------------------------------
    def volver_menu_principal(self):
        """Cerrar la ventana y mostrar el menú principal"""
        self.logger.info("Cerrando módulo de reportes y volviendo al menú principal...")
        if self.parent():
            self.parent().show()
        self.close()