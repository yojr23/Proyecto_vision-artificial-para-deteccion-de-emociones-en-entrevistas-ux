import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QMessageBox, QStackedWidget, QFrame, QScrollArea, QPushButton
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPixmap, QPainter

# Importar componentes
from .utils.buttons import ModernButton
from .utils.footer import AnimatedFooter
from .utils.styles import (
    ColorPalette, GradientStyles, CommonStyles, 
    MessageBoxStyles, LayoutSettings, FontSettings
)

from .config_screens.config_pregunta_screen import ConfigPreguntaScreen

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


class ConfigMainWindow(QMainWindow):
    def __init__(self, parent=None, logger=None):
        super().__init__(parent)
        self.logger = logger or logging.getLogger(__name__)
        self.setWindowTitle("Módulo de Configuración - AGRIOT")
        self.resize(1400, 800)

        # Aplicar gradiente verde de fondo global
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {ColorPalette.DARK_GREEN}, 
                    stop:0.3 {ColorPalette.PRIMARY_GREEN},
                    stop:0.7 {ColorPalette.LIGHT_GREEN},
                    stop:1 {ColorPalette.SOFT_GREEN});
            }}
            QStackedWidget {{
                background: transparent;
                border: none;
            }}
        """)

        self.setup_ui()

    # ------------------------------------------------------------------
    # 🔹 Construcción de la interfaz
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

        # 🔸 Header
        header_frame = self.create_header_frame()
        main_layout.addWidget(header_frame)
        
        # 🔸 Menú inferior
        menu_frame = self.create_menu_frame()
        main_layout.addWidget(menu_frame)

        # 🔸 Stack de pantallas
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
            }}
        """)
        stack_layout = QVBoxLayout(stack_frame)
        stack_layout.setContentsMargins(25, 25, 25, 25)
        self.stack = QStackedWidget()
        stack_layout.addWidget(self.stack)
        main_layout.addWidget(stack_frame, stretch=1)
        
        # Agregar subpantallas al stack
        self.pregunta_screen = ConfigPreguntaScreen(logger=self.logger, parent=self)
        self.stack.addWidget(self.pregunta_screen)

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
            }}
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(12)
        header_layout.setContentsMargins(30, 20, 30, 20)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icono decorativo superior
        icon_label = QLabel("⚙️🌾🔧")
        icon_label.setFont(QFont("Arial", 24))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background: transparent;
                padding: 5px;
            }
        """)
        header_layout.addWidget(icon_label)

        # Título principal
        title = QLabel("Centro de Configuración AGRIOT")
        title.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background: transparent;
                padding: 15px 30px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                letter-spacing: 1.5px;
                border-bottom: 3px solid rgba(255, 255, 255, 0.5);
            }
        """)
        header_layout.addWidget(title)

        # Subtítulo
        subtitle = QLabel("Personaliza y ajusta los parámetros del sistema de entrevistas")
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

    def create_menu_frame(self):
        """Crear frame para menú inferior con 3 botones"""
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
            }}
        """)
        menu_layout = QHBoxLayout(menu_frame)
        menu_layout.setAlignment(Qt.AlignCenter)
        menu_layout.setSpacing(25)

        # Botones principales
        btn_preguntas = ModernButton("❓ Configurar Preguntas", button_type="primary")
        btn_mas_opciones = ModernButton("⚙️ Más Opciones", button_type="secondary")
        btn_volver = ModernButton("🏠 Volver al Menú", button_type="accent")

        # Estilo para botones secundarios
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
                box-shadow: 0 4px 15px rgba(124, 179, 66, 0.2);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(232, 245, 233, 0.95),
                    stop:1 rgba(220, 240, 220, 0.9));
                border: 2px solid #4caf50;
                color: #0d47a1;
                box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(200, 230, 201, 0.95),
                    stop:1 rgba(180, 220, 180, 0.9));
                color: #08306b;
            }
        """

        # Estilo especial para botón primario
        primary_button_style = """
            QPushButton {
                color: #ffffff;
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
                color: #f1f8e9;
                box-shadow: 0 7px 22px rgba(92, 184, 96, 0.6);
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
        btn_preguntas.setStyleSheet(primary_button_style)
        btn_mas_opciones.setStyleSheet(button_styles)
        btn_volver.setStyleSheet(button_styles)

        # Conectar botones
        btn_preguntas.clicked.connect(lambda: self.stack.setCurrentWidget(self.pregunta_screen))
        btn_mas_opciones.clicked.connect(self.mostrar_mas_opciones)
        btn_volver.clicked.connect(self.volver_menu_principal)

        # Agregar botones al layout
        menu_layout.addWidget(btn_preguntas)
        menu_layout.addWidget(btn_mas_opciones)
        menu_layout.addWidget(btn_volver)

        return menu_frame

    def mostrar_mas_opciones(self):
        """Mostrar mensaje temporal para futuras opciones"""
        self.show_info("Próximamente se agregarán más opciones de configuración.")

    # ------------------------------------------------------------------
    # 🔹 Volver al menú principal
    # ------------------------------------------------------------------
    def volver_menu_principal(self):
        """Cerrar la ventana y mostrar el menú principal"""
        self.logger.info("Cerrando módulo de configuración y volviendo al menú principal...")
        if self.parent():
            self.parent().show()
        self.close()
        
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