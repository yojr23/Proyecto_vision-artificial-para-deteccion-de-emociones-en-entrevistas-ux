from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpacerItem, QSizePolicy, QPushButton, QScrollArea, QFrame
)
from PySide6.QtCore import Qt
from ..utils.styles import ColorPalette, GradientStyles
from ..utils.buttons import ModernButton

class UXAgricolaScreen(QMainWindow):
    """Pantalla de UX Agrícola Inclusiva Mejorada"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.setup_window()
        self.setup_ui()
        
    def setup_window(self):
        self.setWindowTitle("AGRIOT - UX Agrícola Inclusiva")
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

        # Contexto y datos clave
        scroll_layout.addLayout(self.create_context_cards())

        # Secciones de herramientas y metodología
        scroll_layout.addLayout(self.create_tools_section())
        scroll_layout.addLayout(self.create_methodology_section())

        # Resultados esperados
        scroll_layout.addLayout(self.create_results_section())

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

        icon = QLabel("📊")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 80px;")
        layout.addWidget(icon)

        title = QLabel("UX Agrícola Inclusiva")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"font-size:48px; font-weight:bold; color:{ColorPalette.DEEP_GREEN};")
        layout.addWidget(title)

        subtitle = QLabel(
            "Herramientas especializadas para medir usabilidad en entornos rurales y campesinos"
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
            ("👩‍🌾 Mujeres", "Activas en agricultura y decisiones locales"),
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

    def create_tools_section(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        title = QLabel("🛠 Herramientas Inclusivas")
        title.setStyleSheet(f"font-size:28px; font-weight:bold; color:{ColorPalette.DEEP_GREEN};")
        layout.addWidget(title)
        tools = [
            "• Evaluación de usabilidad adaptada a contextos rurales",
            "• Tests con poblaciones campesinas",
            "• Métricas de accesibilidad para baja conectividad",
            "• Análisis de patrones de interacción agrícolas",
            "• Prototipado para dispositivos móviles básicos"
        ]
        for t in tools:
            lbl = QLabel(t)
            lbl.setStyleSheet("font-size:16px; color:#556B2F;")
            layout.addWidget(lbl)
        return layout

    def create_methodology_section(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        title = QLabel("📐 Metodología Participativa")
        title.setStyleSheet(f"font-size:28px; font-weight:bold; color:{ColorPalette.DEEP_GREEN};")
        layout.addWidget(title)
        methodologies = [
            "• Co-diseño con comunidades agrícolas",
            "• Pruebas en campo en condiciones reales",
            "• Evaluación iterativa con feedback continuo",
            "• Adaptación a diversidad cultural y educativa",
            "• Enfoque centrado en la experiencia campesina"
        ]
        for m in methodologies:
            lbl = QLabel(m)
            lbl.setStyleSheet("font-size:16px; color:#556B2F;")
            layout.addWidget(lbl)
        return layout

    def create_results_section(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        title = QLabel("🏆 Resultados Esperados")
        title.setStyleSheet(f"font-size:28px; font-weight:bold; color:{ColorPalette.DEEP_GREEN};")
        layout.addWidget(title)
        results = [
            "• Datos sobre la interacción de usuarias rurales",
            "• Recomendaciones para mejorar UX en apps agrícolas",
            "• Validación de herramientas inclusivas",
            "• Guía metodológica para evaluación participativa",
        ]
        for r in results:
            lbl = QLabel(r)
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
