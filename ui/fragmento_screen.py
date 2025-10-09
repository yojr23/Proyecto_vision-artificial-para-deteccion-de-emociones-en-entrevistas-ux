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
from .fragmento_screens.fragmento_info_screen import FragmentoInfoScreen
from .fragmento_screens.fragmento_generar_screen import FragmentoGenerarScreen
from .fragmento_screens.fragmento_fragmentos_screen import FragmentoFragmentosScreen

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


class FragmentoMainWindow(QMainWindow):
    def __init__(self, parent=None, logger=None):
        super().__init__(parent)
        self.logger = logger or logging.getLogger(__name__)
        self.setWindowTitle("Módulo de Fragmentos - AGRIOT")
        self.resize(1400, 800)

        # Aplicar gradiente verde de fondo global con textura de campo
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

        self._check_directories()
        self.setup_ui()

    def load_fragmento_data(self):
            """Cargar datos globales de videos, marcas y fragmentos."""
            try:
                from classes.marcas import Marcas  
                from classes.fragmento import Fragmento 
                import json, os
                from datetime import datetime
                import cv2

                data = {"videos": [], "marcas": {}, "fragmentos": []}
                videos_path = Path("data/videos_originales")
                marcas_path = Path("data/marcas")
                fragmentos_path = Path("data/fragmentos")

                # 🔹 Recorrer videos
                for video_file in videos_path.glob("*.mp4"):
                    info = {
                        "nombre": video_file.name,
                        "ruta": str(video_file),
                        "tamano": video_file.stat().st_size,
                        "fecha": datetime.fromtimestamp(video_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                    }
                    # Duración
                    cap = cv2.VideoCapture(str(video_file))
                    if cap.isOpened():
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                        info["duracion"] = f"{int(frames/fps)}s" if fps else "N/A"
                    else:
                        info["duracion"] = "N/A"
                    cap.release()
                    data["videos"].append(info)

                    # 🔹 Cargar marcas relacionadas
                    video_id = video_file.stem.replace("entrevista_", "")
                    marcas_file = marcas_path / f"marcas_{video_id}.json"
                    if marcas_file.exists():
                        with open(marcas_file, "r", encoding="utf-8") as f:
                            data["marcas"][video_id] = json.load(f).get("marcas", [])
                    else:
                        data["marcas"][video_id] = []

                # 🔹 Cargar fragmentos existentes
                if fragmentos_path.exists():
                    for frag_file in fragmentos_path.glob("*.mp4"):
                        data["fragmentos"].append({"nombre": frag_file.name, "ruta": str(frag_file)})

                self.data_context = data
                self.logger.info(f"Datos cargados: {len(data['videos'])} videos, {len(data['fragmentos'])} fragmentos.")
                return True

            except Exception as e:
                self.logger.error(f"Error cargando datos del módulo de fragmentos: {str(e)}")
                self.data_context = {"videos": [], "marcas": {}, "fragmentos": []}
                return False

    # ------------------------------------------------------------------
    # 🔹 Verificar carpetas
    # ------------------------------------------------------------------
    def _check_directories(self):
        """Verifica que existan las carpetas necesarias para el módulo de análisis"""
        self.Entrevistas_path = Path("data/entrevistas")
        self.Reportes_path = Path("data/reportes")
        self.Fragmentos_path = Path("data/fragmentos")
        self.Marcas_path = Path("data/marcas")  # Nueva carpeta para marcas

        for path in [self.Entrevistas_path, self.Reportes_path, self.Fragmentos_path, self.Marcas_path]:
            if not path.is_dir():
                path.mkdir(parents=True, exist_ok=True)
                self.logger.warning(f"Directorio creado: {path}")
        
    
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
            }}
        """)
        stack_layout = QVBoxLayout(stack_frame)
        stack_layout.setContentsMargins(25, 25, 25, 25)
        self.stack = QStackedWidget()
        stack_layout.addWidget(self.stack)
        main_layout.addWidget(stack_frame, stretch=1)
        
        
        # Agregar subpantallas
        # Agregar subpantallas al stack
        self.load_fragmento_data()
        self.info_screen = FragmentoInfoScreen(logger=self.logger, data_context=self.data_context, parent=self)
        self.generar_screen = FragmentoGenerarScreen(logger=self.logger, data_context=self.data_context,parent=self)
        self.fragmentos_screen = FragmentoFragmentosScreen(parent=self)
        self.stack.addWidget(self.info_screen)
        self.stack.addWidget(self.generar_screen)
        self.stack.addWidget(self.fragmentos_screen)

        # Verificar si hay videos originales
        if not list(self.Originales_path.glob("*.mp4")):
            no_videos_label = QLabel("🌱 No hay videos originales disponibles. Por favor, realice una entrevista primero.")
            no_videos_label.setFont(QFont("Arial", 14, QFont.Weight.Medium))
            no_videos_label.setAlignment(Qt.AlignCenter)
            no_videos_label.setStyleSheet("""
                QLabel {
                    color: #2d5016;
                    padding: 30px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(255, 255, 255, 0.9),
                        stop:1 rgba(240, 255, 240, 0.9));
                    border-radius: 20px;
                    border: 2px dashed #7cb342;
                    margin: 20px;
                }
            """)
            stack_layout.addWidget(no_videos_label)

        

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
            icon_label = QLabel("🌾🎬🌿")
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

            # Título principal con efecto de texto agrícola
            title = QLabel("Gestor de Fragmentos de Entrevistas")
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

            # Subtítulo con diseño orgánico
            subtitle = QLabel("Herramientas avanzadas para cultivar y analizar clips de entrevistas agrícolas")
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
            }}
        """)
        menu_layout = QHBoxLayout(menu_frame)
        menu_layout.setAlignment(Qt.AlignCenter)
        menu_layout.setSpacing(25)

        # Botones con diseño de hojas y crecimiento
        btn_info = ModernButton("📋 Información de Videos", button_type="secondary")
        btn_generar = ModernButton("✂️ Generar Fragmentos", button_type="primary")
        btn_ver = ModernButton("🎞️ Ver Fragmentos", button_type="secondary")
        btn_volver = ModernButton("🏠 Volver al Menú", button_type="accent")

        # Aplicar estilos mejorados con colores de campo
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

        # Aplicar estilos a los botones
        btn_info.setStyleSheet(button_styles)
        btn_generar.setStyleSheet(primary_button_style)
        btn_ver.setStyleSheet(button_styles)
        btn_volver.setStyleSheet(button_styles)

        # Conectar botones
        btn_info.clicked.connect(lambda: self.stack.setCurrentWidget(self.info_screen))
        btn_generar.clicked.connect(lambda: self.stack.setCurrentWidget(self.generar_screen))
        btn_ver.clicked.connect(lambda: self.stack.setCurrentWidget(self.fragmentos_screen))
        btn_volver.clicked.connect(self.volver_menu_principal)

        # Agregar botones al layout
        for btn in [btn_info, btn_generar, btn_ver, btn_volver]:
            menu_layout.addWidget(btn)

        return menu_frame

    # ------------------------------------------------------------------
    # 🔹 Volver al menú principal
    # ------------------------------------------------------------------
    def volver_menu_principal(self):
        """Cerrar la ventana y mostrar el menú principal"""
        self.logger.info("Cerrando módulo de fragmentos y volviendo al menú principal...")
        if self.parent():
            self.parent().show()
        self.close()