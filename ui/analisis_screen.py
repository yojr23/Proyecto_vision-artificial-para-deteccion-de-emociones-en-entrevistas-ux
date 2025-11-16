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
    MessageBoxStyles, LayoutSettings, FontSettings, ShadowEffects
)

from ui.analisis_screens.analisis_info_screen import AnalisisInfoScreen
from ui.analisis_screens.analisis_generar_screen import AnalisisGenerarScreen
from ui.analisis_screens.analisis_reporte_screen import AnalisisReporteScreen


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

class AnalisisMainWindow(QMainWindow):
    def __init__(self, parent=None, logger=None):
        super().__init__(parent)
        self.logger = logger or logging.getLogger(__name__)
        self.setWindowTitle("Módulo de Análisis de Emociones - AGRIOT")
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

        self._check_directories()  # ✅ ESTE MÉTODO DEBE EXISTIR
        self.data_context = {}  # Se cargará en load_reportes_data
        self.setup_ui()
        self.load_reportes_data()  # Cargar al init

    # ------------------------------------------------------------------
    # 🔹 VERIFICAR DIRECTORIOS (MÉTODO FALTANTE)
    # ------------------------------------------------------------------
    def _check_directories(self):
        """Verificar y crear directorios necesarios para el módulo de análisis"""
        self.Entrevistas_path = Path("data/entrevistas")
        self.Reportes_path = Path("data/reportes")
        self.Fragmentos_path = Path("data/fragmentos")

        for path in [self.Entrevistas_path, self.Reportes_path, self.Fragmentos_path]:
            if not path.is_dir():
                path.mkdir(parents=True, exist_ok=True)  # Crea si no existe
                self.logger.warning(f"Directorio creado: {path}")

    # ------------------------------------------------------------------
    # 🔹 CARGAR DATOS DE REPORTES/ENTREVISTAS
    # ------------------------------------------------------------------
    def load_reportes_data(self):
        """Cargar datos globales de entrevistas, reportes y fragmentos."""
        try:
            data = {"entrevistas": [], "reportes": {}, "fragmentos": []}
            
            # 🔹 Recorrer entrevistas
            entrevistas_path = Path("data/entrevistas")
            if entrevistas_path.exists():
                for entrevista_file in entrevistas_path.glob("*.json"):
                    try:
                        with open(entrevista_file, "r", encoding="utf-8") as f:
                            entrevista_data = json.load(f)
                        data["entrevistas"].append({
                            "id": entrevista_file.stem,
                            "ruta": str(entrevista_file),
                            "fecha": entrevista_data.get("creado_en", "N/A"),
                            "total_preguntas": entrevista_data.get("total_preguntas", 0)
                        })
                    except Exception as e:
                        self.logger.warning(f"Error cargando entrevista {entrevista_file}: {e}")

            # 🔹 Recorrer reportes
            reportes_path = Path("data/reportes")
            if reportes_path.exists():
                for reporte_file in reportes_path.glob("*.json"):
                    try:
                        with open(reporte_file, "r", encoding="utf-8") as f:
                            reporte_data = json.load(f)
                        data["reportes"][reporte_file.stem] = reporte_data
                    except Exception as e:
                        self.logger.warning(f"Error cargando reporte {reporte_file}: {e}")

            # 🔹 Recorrer fragmentos
            fragmentos_path = Path("data/fragmentos")
            if fragmentos_path.exists():
                for fragmento_file in fragmentos_path.glob("*.mp4"):
                    data["fragmentos"].append({
                        "nombre": fragmento_file.name,
                        "ruta": str(fragmento_file)
                    })

            self.data_context = data
            self.logger.info(f"Datos cargados: {len(data['entrevistas'])} entrevistas, {len(data['reportes'])} reportes, {len(data['fragmentos'])} fragmentos.")
            return True

        except Exception as e:
            self.logger.error(f"Error cargando datos del módulo de análisis: {str(e)}")
            self.data_context = {"entrevistas": [], "reportes": {}, "fragmentos": []}
            return False

    # ------------------------------------------------------------------
    # 🔹 CONSTRUCCIÓN DE LA INTERFAZ
    # ------------------------------------------------------------------
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
            }}
        """)
        ShadowEffects.apply_green_shadow(stack_frame, blur=45, offset_y=18, opacity=80)
        stack_layout = QVBoxLayout(stack_frame)
        stack_layout.setContentsMargins(25, 25, 25, 25)
        self.stack = QStackedWidget()
        stack_layout.addWidget(self.stack)
        main_layout.addWidget(stack_frame, stretch=1)
        
        # Agregar subpantallas
        # Agregar subpantallas al stack
        self.load_reportes_data()
        self.info_screen = AnalisisInfoScreen(logger=self.logger, data_context=self.data_context, parent=self)
        self.generar_screen = AnalisisGenerarScreen(logger=self.logger, data_context=self.data_context,parent=self)
        self.reporte_sencillo_screen = AnalisisReporteScreen(logger=self.logger, data_context=self.data_context,parent=self)
        self.stack.addWidget(self.info_screen)
        self.stack.addWidget(self.generar_screen)
        self.stack.addWidget(self.reporte_sencillo_screen)


        # 🔸 Footer
        footer = AnimatedFooter(100)
        main_layout.addWidget(footer)

        # Asignar scroll como contenido central
        central_widget = QWidget()
        layout_container = QVBoxLayout(central_widget)
        layout_container.addWidget(scroll_area)
        self.setCentralWidget(central_widget)

    # ------------------------------------------------------------------
    # 🔹 HEADER FRAME
    # ------------------------------------------------------------------
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
            }}
        """)
        ShadowEffects.apply_green_shadow(header_frame, blur=40, offset_y=14, opacity=90)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(12)
        header_layout.setContentsMargins(30, 20, 30, 20)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icono decorativo superior
        icon_label = QLabel("📊🌱📈")
        icon_label.setFont(QFont("Arial", 24))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                color: black;
                background: transparent;
                padding: 5px;
            }
        """)
        header_layout.addWidget(icon_label)

        # Título principal con efecto de texto agrícola
        title = QLabel("Análisis de Emociones en Entrevistas")
        title.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: black;
                background: transparent;
                padding: 15px 30px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                letter-spacing: 1.5px;
                border-bottom: 3px solid rgba(255, 255, 255, 0.5);
            }
        """)
        header_layout.addWidget(title)

        # Subtítulo con diseño orgánico
        subtitle = QLabel("Analiza emociones, genera reportes y obtén insights de las entrevistas agrícolas")
        subtitle.setFont(QFont("Segoe UI", 16, QFont.Weight.Medium))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: #e8f5e9;
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

    # ------------------------------------------------------------------
    # 🔹 MENU FRAME
    # ------------------------------------------------------------------
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
            }}
        """)
        ShadowEffects.apply_shadow(menu_frame, blur=35, offset_y=12, color=(34, 139, 34, 60))
        menu_layout = QHBoxLayout(menu_frame)
        menu_layout.setAlignment(Qt.AlignCenter)
        menu_layout.setSpacing(25)

        # Botones con diseño de hojas y crecimiento
        btn_selector = ModernButton("📋 Seleccionar Entrevistas", button_type="secondary")
        btn_analizar = ModernButton("🔍 Analizar Emociones", button_type="primary")
        btn_reportes = ModernButton("📊 Generar Reportes", button_type="secondary")
        btn_volver = ModernButton("🏠 Volver al Menú", button_type="accent")

        # Estilos de botones
        button_styles = """
            QPushButton {
                color: #1a237e;
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
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(232, 245, 233, 0.95),
                    stop:1 rgba(220, 240, 220, 0.9));
                border: 2px solid #4caf50;
                color: #0d47a1;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(200, 230, 201, 0.95),
                    stop:1 rgba(180, 220, 180, 0.9));
                color: #08306b;
            }
        """

        primary_button_style = """
            QPushButton {
                color: black;
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
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5cb860,
                    stop:0.3 #54ae58,
                    stop:0.7 #4c9c50,
                    stop:1 #448b48);
                border: 2px solid #388e3c;
                color: #f1f8e9;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d8b40,
                    stop:0.3 #378035,
                    stop:0.7 #317534,
                    stop:1 #2b662e);
                color: #e8f5e9;
            }
        """

        # Aplicar estilos
        for btn in [btn_selector, btn_reportes, btn_volver]:
            btn.setStyleSheet(button_styles)
        btn_analizar.setStyleSheet(primary_button_style)

        # Conectar botones (stub - implementar según necesidades)
        btn_selector.clicked.connect(lambda: self.stack.setCurrentWidget(self.info_screen))
        btn_analizar.clicked.connect(lambda: self.stack.setCurrentWidget(self.generar_screen))
        btn_reportes.clicked.connect(lambda: self.stack.setCurrentWidget(self.reporte_sencillo_screen))
        btn_volver.clicked.connect(self.volver_menu_principal)

        # Agregar botones al layout
        for btn in [btn_selector, btn_analizar, btn_reportes, btn_volver]:
            menu_layout.addWidget(btn)

        return menu_frame

   

    # ------------------------------------------------------------------
    # 🔹 MÉTODOS DE BOTONES (STUB - IMPLEMENTAR SEGÚN NECESIDADES)
    # ------------------------------------------------------------------
    def mostrar_selector(self):
        """Mostrar selector de entrevistas"""
        self.show_info("Funcionalidad de selector de entrevistas")

    def analizar_emociones(self):
        """Analizar emociones en las entrevistas seleccionadas"""
        self.show_info("Funcionalidad de análisis de emociones")

    def generar_reportes(self):
        """Generar reportes de análisis"""
        self.show_info("Funcionalidad de generación de reportes")
    
    # ------------------------------------------------------------------
    # 🔹 UTILIDADES
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

    def show_info(self, msg):
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Información")
        msgbox.setText(msg)
        msgbox.setIcon(QMessageBox.Information)
        msgbox.setStyleSheet("""
            QLabel { 
                color: black;
                background-color: white; 
            }
        """)
        msgbox.exec()
        self.logger.info(msg)

    # ------------------------------------------------------------------
    # 🔹 VOLVER AL MENÚ PRINCIPAL
    # ------------------------------------------------------------------
    def volver_menu_principal(self):
        """Cerrar la ventana y mostrar el menú principal"""
        self.logger.info("Cerrando módulo de análisis y volviendo al menú principal...")
        if self.parent():
            self.parent().show()
        self.close()
