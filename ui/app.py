import sys
import logging
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpacerItem, QSizePolicy, QMessageBox, QInputDialog, QPushButton, QFileDialog,

)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QFont, QCursor

# Importar componentes modulares
from .utils.animations import AnimatedLabel, TitleAnimator
from .utils.cards import FloatingCard, InfoCard, MascotCard
from .utils.buttons import ModernButton
from .utils.footer import AnimatedFooter
from .utils.styles import (
    ColorPalette, GradientStyles, CommonStyles, 
    MessageBoxStyles, LayoutSettings, FontSettings
)
from ui.interview_screen import InterviewScreen
from ui.fragmento_screen import FragmentoMainWindow

from ui.interviewee_screen import IntervieweeScreen, DataBridge

from .informacion_adicional.deteccion_screen import DeteccionScreen
from .informacion_adicional.ux_agricola_screen import UXAgricolaScreen
from .informacion_adicional.transformacion_screen import TransformacionScreen

class App(QMainWindow):
    """Aplicación principal AGRIOT con arquitectura modular"""
    
    def __init__(self, logger=None):
        super().__init__()
        self.logger = logger or logging.getLogger(__name__)
        self.setupWindow()
        self.setupMainWidget()
        self.initializeAnimations()
        
    def setupWindow(self):
        """Configuración inicial de la ventana"""
        self.setWindowTitle("AGRIOT - Semillero de Innovación Agrícola UX")
        self.setGeometry(100, 100, 1600, 1000)
        self.setMinimumSize(1400, 900)
        # Aplica el gradiente a toda la app, incluyendo scrollarea
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background: {GradientStyles.background_gradient()};
            }}
            QScrollArea {{
                background: transparent;
                border: none;
            }}
        """)
        
    def setupMainWidget(self):
        """Configurar widget central y layout principal con scroll"""
        from PySide6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        central_widget = QWidget()
        scroll.setWidget(central_widget)
        self.setCentralWidget(scroll)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(60, 20, 60, 20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Construir interfaz por secciones
        self.buildHeader(main_layout)
        self.buildFeatureSection(main_layout)
        self.buildMainContentSection(main_layout)
        self.buildActionButtonsSection(main_layout)
        self.buildFooter(main_layout)
        
    def buildHeader(self, parent_layout):
        """Construir sección de header con título animado"""
        header_frame = QWidget()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(5)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Título principal animado
        self.main_title = AnimatedLabel("AGRIOT")
        self.main_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        TitleAnimator.setupTitleShadow(self.main_title)
        # Ajustar color del texto a un verde oscuro o negro para contraste
        self.main_title.setStyleSheet(f"""
            QLabel {{
                font-size: 64px;
                font-weight: bold;
                color: {ColorPalette.DEEP_GREEN if hasattr(ColorPalette, 'DEEP_GREEN') else '#222'};
                letter-spacing: 6px;
                text-shadow: 2px 2px 8px rgba(0,0,0,0.18);
                background: transparent;
            }}
        """)
        header_layout.addWidget(self.main_title)

        # Subtítulo descriptivo
        subtitle = self.createSubtitle()
        subtitle.setContentsMargins(0, 0, 0, 0)
        header_layout.addWidget(subtitle)

        parent_layout.addWidget(header_frame)
        
    def createSubtitle(self):
        """Crear subtítulo con estilo"""
        subtitle = QLabel("🌱 Semillero de Innovación • Experiencia de Usuario Agrícola • Empoderamiento Digital 🌾")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"""
            QLabel {{
                font-size: 20px;
                color: {ColorPalette.DARK_OLIVE};
                font-weight: 400;
                font-style: italic;
                padding: 8px 30px 8px 30px;
                margin-top: 0px;
                margin-bottom: 0px;
                letter-spacing: 2px;
                border-radius: 20px;
                background: {ColorPalette.TRANSPARENT_GREEN};
                border: 1px solid rgba(50, 205, 50, 0.3);
            }}
        """)
        return subtitle
        
    def buildFeatureSection(self, parent_layout):
        """Construir sección de características con cards estáticas y iconos clickeables"""
        from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QPoint
        features_frame = QWidget()
        features_layout = QHBoxLayout(features_frame)
        features_layout.setSpacing(30)
        features_layout.setContentsMargins(0, 0, 0, 0)
        features_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Datos estáticos de las cartas
        static_cards = [
            {"icon": "🤖", "title": "Detección Emocional IA", "desc": "Análisis avanzado de expresiones faciales para evaluar la experiencia del usuario en tiempo real", "screen": "deteccion"},
            {"icon": "📊", "title": "UX Agrícola Inclusiva", "desc": "Herramientas especializadas para medir usabilidad en entornos rurales y campesinos", "screen": "ux_agricola"},
            {"icon": "🚀", "title": "Transformación Digital", "desc": "Empoderando a mujeres campesinas mediante tecnología accesible e intuitiva", "screen": "transformacion"},
        ]

        for card in static_cards:
            card_widget = QWidget()
            card_widget.setFixedSize(320, 220)
            card_layout = QVBoxLayout(card_widget)
            card_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            card_layout.setSpacing(12)
            card_layout.setContentsMargins(24, 18, 24, 18)

            # Icono clickeable (botón)
            icon_button = QPushButton(card["icon"])
            icon_button.setCursor(QCursor(Qt.PointingHandCursor))
            icon_button.setFixedSize(80, 80)
            icon_button.setStyleSheet(f"""
                QPushButton {{
                    font-size: 54px;
                    color: {ColorPalette.DEEP_GREEN if hasattr(ColorPalette, 'DEEP_GREEN') else '#1a3d1a'};
                    background: transparent;
                    border-radius: 40px;
                    border: 2px solid transparent;
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background: rgba(50, 205, 50, 0.1);
                    border: 2px solid rgba(50, 205, 50, 0.3);
                    transform: scale(1.05);
                }}
                QPushButton:pressed {{
                    background: rgba(50, 205, 50, 0.2);
                    border: 2px solid rgba(50, 205, 50, 0.5);
                }}
            """)
            
            # Conectar el botón a la función correspondiente
            if card["screen"] == "deteccion":
                icon_button.clicked.connect(self.open_deteccion)
            elif card["screen"] == "ux_agricola":
                icon_button.clicked.connect(self.open_ux_agricola)
            elif card["screen"] == "transformacion":
                icon_button.clicked.connect(self.open_transformacion)

            card_layout.addWidget(icon_button, alignment=Qt.AlignmentFlag.AlignCenter)

            # Título limpio
            title_label = QLabel(card["title"])
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet(f"""
                font-size: 22px;
                font-weight: bold;
                color: {ColorPalette.DEEP_GREEN if hasattr(ColorPalette, 'DEEP_GREEN') else '#1a3d1a'};
                letter-spacing: 1px;
                background: transparent;
                text-shadow: 1px 1px 6px rgba(0,0,0,0.08);
                border: none;
            """)
            card_layout.addWidget(title_label)

            # Descripción limpia
            desc_label = QLabel(card["desc"])
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet(f"""
                font-size: 15px;
                color: {ColorPalette.DARK_OLIVE if hasattr(ColorPalette, 'DARK_OLIVE') else '#333'};
                background: transparent;
                border: none;
                padding: 0 2px;
            """)
            card_layout.addWidget(desc_label)

            # Estilo de la card (usando gradiente y bordes del proyecto)
            card_widget.setStyleSheet(f"""
                background: {GradientStyles.background_gradient() if hasattr(GradientStyles, 'background_gradient') else 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e8f5e9, stop:1 #f1f8e9)'};
                border-radius: 22px;
                border: 2px solid {ColorPalette.LIGHT_GREEN if hasattr(ColorPalette, 'LIGHT_GREEN') else '#b2dfdb'};
                box-shadow: 0 4px 18px rgba(60,120,60,0.08);
            """)
            features_layout.addWidget(card_widget, alignment=Qt.AlignmentFlag.AlignTop)

        parent_layout.addWidget(features_frame)
        
    # getFeatureCardsData eliminado: ahora las cartas son estáticas y animadas
        
    def buildMainContentSection(self, parent_layout):
        """Construir sección principal con información y mascota"""
        content_frame = QWidget()
        content_layout = QHBoxLayout(content_frame)
        content_layout.setSpacing(30)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Panel de información
        info_panel = InfoCard(width=600)
        content_layout.addWidget(info_panel, alignment=Qt.AlignmentFlag.AlignTop)

        # Panel de mascota
        mascot_panel = self.createMascotPanel()
        content_layout.addWidget(mascot_panel, alignment=Qt.AlignmentFlag.AlignTop)

        parent_layout.addWidget(content_frame)
        
    def createMascotPanel(self):
        """Crear panel de mascota con animaciones"""
        mascot_frame = QWidget()
        mascot_frame.setFixedWidth(500)
        mascot_layout = QVBoxLayout(mascot_frame)
        mascot_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mascot_layout.setSpacing(LayoutSettings.LARGE_SPACING)
        
        # Contenedor circular para mascota
        self.mascot_container = MascotCard(size=380)
        container_layout = QVBoxLayout(self.mascot_container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Imagen/placeholder de mascota
        self.mascot_image = self.createMascotImage()
        container_layout.addWidget(self.mascot_image)
        
        # Configurar animación de rebote
        self.mascot_container.enterEvent = lambda event: self.mascot_image.startBounceAnimation()
        
        mascot_layout.addWidget(self.mascot_container)
        
        # Etiqueta descriptiva
        mascot_label = self.createMascotLabel()
        mascot_layout.addWidget(mascot_label)
        
        return mascot_frame
        
    def createMascotImage(self):
        """Crear imagen de mascota o placeholder"""
        import os
        mascot_image = AnimatedLabel()
        img_path = "img/semillin.png"
        pixmap = QPixmap(img_path)
        if not os.path.exists(img_path) or pixmap.isNull():
            mascot_image.setText("⚠️\nSin imagen\nAGRIOT")
            mascot_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
            mascot_image.setStyleSheet(f"""
                QLabel {{
                    color: {ColorPalette.DARK_GREEN};
                    font-size: 38px;
                    font-weight: bold;
                    line-height: 1.3;
                    background: {GradientStyles.radial_gradient()};
                    border-radius: 30px;
                }}
            """)
        else:
            scaled_pixmap = pixmap.scaled(
                320, 320, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            mascot_image.setPixmap(scaled_pixmap)
            mascot_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return mascot_image
        
    def createMascotLabel(self):
        """Crear etiqueta descriptiva de la mascota"""
        mascot_label = QLabel("🌟 Tu Asistente AGRIOT 🌟")
        mascot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mascot_label.setStyleSheet(f"""
            QLabel {{
                font-size: 22px;
                font-weight: 600;
                color: {ColorPalette.DEEP_GREEN};
                padding: 15px 30px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 rgba(50, 205, 50, 0.2), stop:1 rgba(144, 238, 144, 0.2));
                border-radius: 25px;
                border: 2px solid rgba(50, 205, 50, 0.3);
                letter-spacing: 1px;
            }}
        """)
        return mascot_label
        
    def buildActionButtonsSection(self, parent_layout):
        """Construir sección de botones de acción"""
        buttons_section = QWidget()
        buttons_layout = QVBoxLayout(buttons_section)
        buttons_layout.setSpacing(10)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Título de sección
        buttons_title = self.createButtonsSectionTitle()
        buttons_layout.addWidget(buttons_title)

        # Grid de botones
        buttons_grid = self.createButtonsGrid()
        buttons_layout.addLayout(buttons_grid)

        parent_layout.addWidget(buttons_section)
        
    def createButtonsSectionTitle(self):
        """Crear título de sección de botones"""
        buttons_title = QLabel("🎮 Panel de Control AGRIOT")
        buttons_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        buttons_title.setStyleSheet(CommonStyles.title_style(font_size=26))
        buttons_title.setContentsMargins(0, 0, 0, 0)
        return buttons_title
        
    def createButtonsGrid(self):
        """Crear grid con botones de acción (estáticos)"""
        buttons_grid = QHBoxLayout()
        buttons_grid.setSpacing(30)
        buttons_grid.setContentsMargins(0, 0, 0, 0)
        buttons_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Botón: Configurar Sistema
        btn_config = ModernButton(
            text="Configurar Sistema",
            button_type="secondary",
            icon_text="⚡"
        )
        btn_config.setFixedSize(220, 60)
        btn_config.clicked.connect(self.open_config)
        buttons_grid.addWidget(btn_config, alignment=Qt.AlignmentFlag.AlignTop)

        # Botón: Iniciar Entrevista
        btn_entrevista = ModernButton(
            text="Iniciar Entrevista",
            button_type="primary",
            icon_text="📝"
        )
        btn_entrevista.setFixedSize(220, 60)
        btn_entrevista.clicked.connect(self.open_entrevista)
        buttons_grid.addWidget(btn_entrevista, alignment=Qt.AlignmentFlag.AlignTop)


        # Botón: Iniciar Entrevista
        btn_previsualizacion = ModernButton(
            text="Previsualización\nde Fragmentos",
            button_type="primary",
            icon_text="🎥"
        )
        btn_previsualizacion.setFixedHeight(60)
        btn_previsualizacion.setMinimumWidth(220)
        btn_previsualizacion.setMaximumWidth(340)
        btn_previsualizacion.clicked.connect(self.open_previsualizacion)
        # Ajustar el texto para que se muestre centrado en dos líneas
        btn_previsualizacion.setStyleSheet(btn_previsualizacion.styleSheet() + """
            QPushButton {
            text-align: center;
            padding-top: 8px;
            padding-bottom: 8px;
            line-height: 1.2;
            }
        """)
        buttons_grid.addWidget(btn_previsualizacion, alignment=Qt.AlignmentFlag.AlignTop)

        # Botón: Generar Análisis
        btn_analisis = ModernButton(
            text="Generar Análisis",
            button_type="primary",
            icon_text="📈"
        )
        btn_analisis.setFixedSize(220, 60)
        btn_analisis.clicked.connect(self.open_analisis)
        buttons_grid.addWidget(btn_analisis, alignment=Qt.AlignmentFlag.AlignTop)

        # Botón: Ver Resultados
        btn_resultados = ModernButton(
            text="Ver Resultados",
            button_type="secondary",
            icon_text="📊"
        )
        btn_resultados.setFixedSize(220, 60)
        btn_resultados.clicked.connect(self.open_ver_reportes)
        buttons_grid.addWidget(btn_resultados, alignment=Qt.AlignmentFlag.AlignTop)

        return buttons_grid
        
    # getButtonsData eliminado: los botones ahora son estáticos
    def open_entrevista(self):
        """Abrir pantalla de entrevista"""
        self.logger.info("Navegando a pantalla de Entrevista")
        
        try:
            
            # Importar y crear la pantalla de entrevista
            self.entrevista_window = InterviewScreen()
            self.entrevista_window.show()
            
        except ImportError as e:
            self.logger.error(f"Error al importar InterviewScreen: {e}")
            QMessageBox.critical(self, "Error", "No se pudo cargar la pantalla de entrevista")
        except Exception as e:
            self.logger.error(f"Error al abrir entrevista: {e}")
            QMessageBox.critical(self, "Error", f"Error al abrir la pantalla: {str(e)}")
                
    def open_previsualizacion(self):
        """Abrir módulo de fragmentos como ventana separada"""
        self.logger.info("Abriendo ventana del módulo de fragmentos...")
        try:
            from ui.fragmento_screen import FragmentoMainWindow
            
            # Ocultar la ventana principal
            self.hide()
            
            # Crear y mostrar la ventana del módulo de fragmentos
            self.fragmento_window = FragmentoMainWindow(parent=self,logger=self.logger)
            self.fragmento_window.show()
        except Exception as e:
            self.logger.error(f"Error al abrir módulo de fragmentos: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo abrir el módulo de fragmentos: {e}")

    def open_deteccion(self):
        """Abrir pantalla de Detección Emocional IA"""
        self.logger.info("Navegando a pantalla de Detección Emocional IA")
        try:
            self.deteccion_window = DeteccionScreen(parent=self)
            self.deteccion_window.show()
            self.hide()
        except Exception as e:
            self.logger.error(f"Error al abrir pantalla de detección: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo abrir la pantalla: {str(e)}")

    def open_ux_agricola(self):
        """Abrir pantalla de UX Agrícola Inclusiva"""
        self.logger.info("Navegando a pantalla de UX Agrícola Inclusiva")
        try:
            self.ux_agricola_window = UXAgricolaScreen(parent=self)
            self.ux_agricola_window.show()
            self.hide()
        except Exception as e:
            self.logger.error(f"Error al abrir pantalla de UX Agrícola: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo abrir la pantalla: {str(e)}")

    def open_transformacion(self):
        """Abrir pantalla de Transformación Digital"""
        self.logger.info("Navegando a pantalla de Transformación Digital")
        try:
            self.transformacion_window = TransformacionScreen(parent=self)
            self.transformacion_window.show()
            self.hide()
        except Exception as e:
            self.logger.error(f"Error al abrir pantalla de transformación: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo abrir la pantalla: {str(e)}")

                   
    def buildFooter(self, parent_layout):
        """Construir footer con espaciador"""
        # Espaciador antes del footer
        spacer = QSpacerItem(
            20, 30, 
            QSizePolicy.Policy.Minimum, 
            QSizePolicy.Policy.Expanding
        )
        parent_layout.addItem(spacer)
        
        # Footer animado
        footer = AnimatedFooter(height=100)
        parent_layout.addWidget(footer)
        
    def initializeAnimations(self):
        """Inicializar animaciones después de renderizar UI"""
        QTimer.singleShot(500, self._setupAnimations)
        
    def _setupAnimations(self):
        """Configurar animaciones diferidas"""
        try:
            if hasattr(self, 'mascot_image') and self.mascot_image.geometry().isValid():
                self.mascot_image.setOriginalGeometry(self.mascot_image.geometry())
        except Exception as e:
            self.logger.warning(f"No se pudieron inicializar animaciones: {e}")
            
    # Métodos de callback para botones
    # open_entrevista eliminado (login removido)
    
    def open_config(self):
        """Abrir configuración del sistema"""
        self.logger.info("Navegando a configuración del Sistema")
        try:
            from ui.config_screen import ConfigMainWindow
            
            # Ocultar la ventana principal
            self.hide()
            
            # Crear y mostrar la ventana del módulo de fragmentos
            self.config_window = ConfigMainWindow(parent=self,logger=self.logger)
            self.config_window.show()
        except Exception as e:
            self.logger.error(f"Error al abrir módulo de configuracion: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo abrir el módulo de configuracion: {e}")

    
    def open_analisis(self):
        """Generar análisis y reportes"""
        self.logger.info("Generando Análisis")
        try:
            from ui.analisis_screen import AnalisisMainWindow
            
            # Ocultar la ventana principal
            self.hide()
            
            # Crear y mostrar la ventana del módulo de fragmentos
            self.analisis_window = AnalisisMainWindow(parent=self,logger=self.logger)
            self.analisis_window.show()
        except Exception as e:
            self.logger.error(f"Error al abrir módulo de analisis: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo abrir el módulo de analisis: {e}")

    
    def open_ver_reportes(self):
        """Ver reportes y resultados"""
        self.logger.info("Ver Reportes y Resultados")
        try:
            from ui.reportes_screen import ReportesMainWindow
            
            # Ocultar la ventana principal
            self.hide()
            
            # Crear y mostrar la ventana del módulo de fragmentos
            self.reportes_window = ReportesMainWindow(parent=self,logger=self.logger)
            self.reportes_window.show()
        except Exception as e:
            self.logger.error(f"Error al abrir módulo de reportes: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo abrir el módulo de reportes: {e}")

        
    
    def showStyledMessage(self, title, message):
        """Mostrar mensaje personalizado con estilo coherente"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet(MessageBoxStyles.get_modern_messagebox_style())
        msg.exec()
    
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