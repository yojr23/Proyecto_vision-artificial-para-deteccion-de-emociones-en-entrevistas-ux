from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpacerItem, QSizePolicy, QPushButton, QScrollArea, QFrame
)
from PySide6.QtCore import Qt
from ..utils.styles import ColorPalette, GradientStyles
from ..utils.buttons import ModernButton

class TransformacionScreen(QMainWindow):
    """Pantalla de Transformación Digital Mejorada"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.setup_window()
        self.setup_ui()
        
    def setup_window(self):
        self.setWindowTitle("AGRIOT - Transformación Digital")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {GradientStyles.background_gradient()};
            }}
        """)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(30)
        scroll_layout.setContentsMargins(40, 40, 40, 40)

        # Header
        scroll_layout.addLayout(self.create_header())

        # Tarjetas de contexto y brechas digitales
        scroll_layout.addLayout(self.create_context_cards())

        # Secciones principales
        scroll_layout.addLayout(self.create_programs_section())
        scroll_layout.addLayout(self.create_impact_section())

        # Botón volver
        scroll_layout.addLayout(self.create_buttons())

        # Spacer final
        scroll_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

    def create_header(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel("🚀")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 80px;")
        layout.addWidget(icon)

        title = QLabel("Transformación Digital")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"font-size:48px; font-weight:bold; color:{ColorPalette.DEEP_GREEN};")
        layout.addWidget(title)

        subtitle = QLabel(
            "Empoderando a mujeres campesinas mediante tecnología accesible e intuitiva"
        )
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("font-size:20px; color:#556B2F; padding:0 100px;")
        layout.addWidget(subtitle)
        return layout

    def create_context_cards(self):
        layout = QHBoxLayout()
        layout.setSpacing(20)
        cards_info = [
            ("🌎 Población", "Los Santos: 15,503 habitantes, 48.7% mujeres"),
            ("📶 Conectividad", "Solo 40% con internet en áreas rurales"),
            ("👩‍🌾 Mujeres", "Activas en agricultura y adopción tecnológica"),
            ("⚠️ Retos", "Baja alfabetización digital y acceso limitado a tecnología")
        ]
        for icon, text in cards_info:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {background: rgba(255,255,255,0.1); border-radius: 20px; padding: 20px;}
            """)
            card_layout = QVBoxLayout(card)
            lbl_icon = QLabel(icon)
            lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_icon.setStyleSheet("font-size:36px;")
            lbl_text = QLabel(text)
            lbl_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_text.setWordWrap(True)
            lbl_text.setStyleSheet("font-size:16px; color:#333;")
            card_layout.addWidget(lbl_icon)
            card_layout.addWidget(lbl_text)
            layout.addWidget(card)
        return layout

    def create_programs_section(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        title = QLabel("🛠 Programas de Empoderamiento")
        title.setStyleSheet(f"font-size:28px; font-weight:bold; color:{ColorPalette.DEEP_GREEN};")
        layout.addWidget(title)
        programs = [
            "• Capacitación en herramientas digitales agrícolas",
            "• Mentoría en emprendimiento tecnológico rural",
            "• Acceso a plataformas de comercialización digital",
            "• Formación en análisis de datos para la agricultura",
            "• Redes de mujeres innovadoras en el sector agrícola"
        ]
        for p in programs:
            lbl = QLabel(p)
            lbl.setStyleSheet("font-size:16px; color:#556B2F;")
            layout.addWidget(lbl)
        return layout

    def create_impact_section(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        title = QLabel("📈 Impacto y Resultados")
        title.setStyleSheet(f"font-size:28px; font-weight:bold; color:{ColorPalette.DEEP_GREEN};")
        layout.addWidget(title)
        impacts = [
            "• +500 mujeres campesinas capacitadas digitalmente",
            "• 85% de aumento en adopción de tecnología agrícola",
            "• 60% de mejora en productividad con herramientas digitales",
            "• Creación de 25 emprendimientos tecnológicos rurales",
            "• Reducción de brecha digital de género en 40%"
        ]
        for i in impacts:
            lbl = QLabel(i)
            lbl.setStyleSheet("font-size:16px; color:#556B2F;")
            layout.addWidget(lbl)
        return layout

    def create_buttons(self):
        layout = QHBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        back_button = ModernButton(
            text="Volver al Inicio",
            button_type="secondary",
            icon_text="🏠"
        )
        back_button.setFixedSize(200, 50)
        back_button.clicked.connect(self.volver_inicio)
        layout.addWidget(back_button)
        return layout

    def volver_inicio(self):
        if self.parent_app:
            self.parent_app.show()
        self.close()
