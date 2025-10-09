from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpacerItem, QSizePolicy, QPushButton, QScrollArea, QFrame, QGridLayout
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
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(255, 255, 255, 0.1);
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: rgba(34, 139, 34, 0.5);
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(34, 139, 34, 0.7);
            }
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(35)
        scroll_layout.setContentsMargins(60, 50, 60, 50)

        # Header
        scroll_layout.addLayout(self.create_header())

        # Contexto del proyecto
        scroll_layout.addWidget(self.create_context_section())

        # Herramientas y Metodología lado a lado
        scroll_layout.addLayout(self.create_tools_methodology_section())

        # Resultados e Impacto
        scroll_layout.addWidget(self.create_results_impact_section())

        # Botón volver
        scroll_layout.addLayout(self.create_buttons())

        # Spacer final
        scroll_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

    def create_header(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel("📊")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 90px;")
        layout.addWidget(icon)

        title = QLabel("UX Agrícola Inclusiva")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 52px; 
            font-weight: bold; 
            color: #000000;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)

        subtitle = QLabel(
            "Herramientas especializadas para medir usabilidad en entornos rurales "
            "con enfoque en mujeres campesinas"
        )
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 22px; 
            color: #000000;
            padding: 0 120px;
            line-height: 1.5;
        """)
        layout.addWidget(subtitle)
        return layout

    def create_context_section(self):
        """Sección de contexto con diseño de grid"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 25px;
                padding: 35px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(25)
        
        # Título
        section_title = QLabel("🌍 Contexto Rural de Los Santos")
        section_title.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold; 
            color: #000000;
            margin-bottom: 10px;
        """)
        section_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(section_title)
        
        # Grid de información
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        
        cards_info = [
            ("🌎", "Población Rural", "15,503 habitantes\n48.7% mujeres (DANE 2024)", "#e3f2fd"),
            ("📶", "Conectividad Digital", "Solo 40% con acceso\na internet", "#fff3e0"),
            ("👩‍🌾", "Rol de Mujeres", "Líderes en agricultura\ny decisiones comunitarias", "#f3e5f5"),
            ("⚠️", "Desafíos Críticos", "Baja alfabetización digital\nAcceso tecnológico limitado", "#ffebee")
        ]
        
        for i, (icon, title, text, color) in enumerate(cards_info):
            row = i // 2
            col = i % 2
            card = self.create_context_card(icon, title, text, color)
            grid_layout.addWidget(card, row, col)
        
        layout.addLayout(grid_layout)
        return container

    def create_context_card(self, icon, title, text, bg_color):
        """Crea una card de contexto con diseño personalizado"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {bg_color};
                border: 2px solid rgba(0, 0, 0, 0.1);
                border-radius: 15px;
                padding: 25px;
            }}
            QFrame:hover {{
                background: {bg_color};
                border: 2px solid rgba(34, 139, 34, 0.4);
                transform: scale(1.02);
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        
        lbl_icon = QLabel(icon)
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setStyleSheet("font-size: 50px;")
        
        lbl_title = QLabel(title)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000;")
        
        lbl_text = QLabel(text)
        lbl_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_text.setWordWrap(True)
        lbl_text.setStyleSheet("font-size: 16px; color: #000000; line-height: 1.4;")
        
        card_layout.addWidget(lbl_icon)
        card_layout.addWidget(lbl_title)
        card_layout.addWidget(lbl_text)
        
        return card

    def create_tools_methodology_section(self):
        """Herramientas y Metodología lado a lado"""
        layout = QHBoxLayout()
        layout.setSpacing(25)
        
        # Herramientas Inclusivas
        tools_container = QFrame()
        tools_container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 25px;
                padding: 30px;
            }
        """)
        
        tools_layout = QVBoxLayout(tools_container)
        tools_layout.setSpacing(20)
        
        tools_title = QLabel("🛠️ Herramientas Inclusivas")
        tools_title.setStyleSheet("font-size: 30px; font-weight: bold; color: #000000;")
        tools_layout.addWidget(tools_title)
        
        tools_desc = QLabel(
            "Instrumentos especializados adaptados a las necesidades "
            "y contextos de las comunidades rurales campesinas"
        )
        tools_desc.setWordWrap(True)
        tools_desc.setStyleSheet("font-size: 16px; color: #000000; margin-bottom: 10px;")
        tools_layout.addWidget(tools_desc)
        
        tools = [
            ("📋", "Evaluación de Usabilidad", "Pruebas adaptadas a contextos rurales y baja conectividad"),
            ("👥", "Tests Participativos", "Sesiones con poblaciones campesinas reales"),
            ("📱", "Métricas de Accesibilidad", "Evaluación para dispositivos móviles básicos"),
            ("🔍", "Análisis de Interacción", "Patrones de uso específicos del sector agrícola"),
            ("🎨", "Prototipado Adaptativo", "Diseños optimizados para baja alfabetización digital")
        ]
        
        for icon, tool_title, tool_desc in tools:
            tool_frame = QFrame()
            tool_frame.setStyleSheet("""
                QFrame {
                    background: rgba(144, 238, 144, 0.15);
                    border-left: 4px solid rgba(34, 139, 34, 0.6);
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            tool_layout = QVBoxLayout(tool_frame)
            tool_layout.setSpacing(5)
            
            tool_header = QLabel(f"{icon} {tool_title}")
            tool_header.setStyleSheet("font-size: 18px; font-weight: bold; color: #000000;")
            
            tool_text = QLabel(tool_desc)
            tool_text.setWordWrap(True)
            tool_text.setStyleSheet("font-size: 15px; color: #000000;")
            
            tool_layout.addWidget(tool_header)
            tool_layout.addWidget(tool_text)
            
            tools_layout.addWidget(tool_frame)
        
        # Metodología Participativa
        methodology_container = QFrame()
        methodology_container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 25px;
                padding: 30px;
            }
        """)
        
        methodology_layout = QVBoxLayout(methodology_container)
        methodology_layout.setSpacing(20)
        
        methodology_title = QLabel("📐 Metodología Participativa")
        methodology_title.setStyleSheet("font-size: 30px; font-weight: bold; color: #000000;")
        methodology_layout.addWidget(methodology_title)
        
        methodology_desc = QLabel(
            "Enfoque colaborativo que integra a las comunidades "
            "en cada etapa del proceso de diseño y evaluación"
        )
        methodology_desc.setWordWrap(True)
        methodology_desc.setStyleSheet("font-size: 16px; color: #000000; margin-bottom: 10px;")
        methodology_layout.addWidget(methodology_desc)
        
        methodologies = [
            ("🤝", "Co-diseño Comunitario", "Diseño colaborativo con comunidades agrícolas locales"),
            ("🌾", "Pruebas en Campo", "Evaluaciones en condiciones reales de trabajo"),
            ("🔄", "Evaluación Iterativa", "Mejora continua con feedback constante de usuarias"),
            ("🌐", "Adaptación Cultural", "Respeto a diversidad educativa y cultural regional"),
            ("💚", "Enfoque Campesino", "Centrado en experiencias y necesidades reales")
        ]
        
        for icon, method_title, method_desc in methodologies:
            method_frame = QFrame()
            method_frame.setStyleSheet("""
                QFrame {
                    background: rgba(173, 216, 230, 0.2);
                    border-left: 4px solid rgba(30, 144, 255, 0.6);
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            method_layout = QVBoxLayout(method_frame)
            method_layout.setSpacing(5)
            
            method_header = QLabel(f"{icon} {method_title}")
            method_header.setStyleSheet("font-size: 18px; font-weight: bold; color: #000000;")
            
            method_text = QLabel(method_desc)
            method_text.setWordWrap(True)
            method_text.setStyleSheet("font-size: 15px; color: #000000;")
            
            method_layout.addWidget(method_header)
            method_layout.addWidget(method_text)
            
            methodology_layout.addWidget(method_frame)
        
        layout.addWidget(tools_container)
        layout.addWidget(methodology_container)
        
        return layout

    def create_results_impact_section(self):
        """Sección de resultados e impacto esperado"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 25px;
                padding: 35px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(25)
        
        # Título principal
        main_title = QLabel("🏆 Resultados e Impacto Esperado")
        main_title.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold; 
            color: #000000;
            margin-bottom: 10px;
        """)
        main_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(main_title)
        
        # Grid 2x2 de resultados
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        
        results = [
            (
                "📊", 
                "Datos de Interacción", 
                "Información detallada sobre cómo las mujeres rurales interactúan con tecnología agrícola",
                "rgba(230, 247, 255, 1)"
            ),
            (
                "💡", 
                "Recomendaciones UX", 
                "Guías prácticas para mejorar usabilidad en aplicaciones del sector agrícola",
                "rgba(255, 248, 225, 1)"
            ),
            (
                "✅", 
                "Validación de Herramientas", 
                "Comprobación de efectividad de instrumentos inclusivos en contextos reales",
                "rgba(237, 247, 237, 1)"
            ),
            (
                "📖", 
                "Guía Metodológica", 
                "Manual completo para evaluación participativa en comunidades rurales campesinas",
                "rgba(255, 235, 238, 1)"
            )
        ]
        
        for i, (icon, title, description, color) in enumerate(results):
            row = i // 2
            col = i % 2
            
            result_card = QFrame()
            result_card.setStyleSheet(f"""
                QFrame {{
                    background: {color};
                    border: 2px solid rgba(34, 139, 34, 0.2);
                    border-radius: 15px;
                    padding: 25px;
                }}
                QFrame:hover {{
                    border: 2px solid rgba(34, 139, 34, 0.5);
                }}
            """)
            
            result_layout = QVBoxLayout(result_card)
            result_layout.setSpacing(10)
            
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 42px;")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            title_label = QLabel(title)
            title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("font-size: 15px; color: #000000; line-height: 1.4;")
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            result_layout.addWidget(icon_label)
            result_layout.addWidget(title_label)
            result_layout.addWidget(desc_label)
            
            grid_layout.addWidget(result_card, row, col)
        
        layout.addLayout(grid_layout)
        
        # Impacto social
        impact_frame = QFrame()
        impact_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(144, 238, 144, 0.3),
                    stop:1 rgba(34, 139, 34, 0.2));
                border: 2px solid rgba(34, 139, 34, 0.4);
                border-radius: 15px;
                padding: 20px;
                margin-top: 10px;
            }
        """)
        
        impact_layout = QVBoxLayout(impact_frame)
        impact_layout.setSpacing(10)
        
        impact_title = QLabel("🌟 Impacto Social")
        impact_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #000000;")
        impact_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        impact_text = QLabel(
            "Este proyecto contribuye a reducir la brecha digital de género en zonas rurales, "
            "empoderando a las mujeres campesinas mediante tecnología accesible e inclusiva que "
            "respeta su contexto cultural y fortalece su participación en la agricultura sostenible."
        )
        impact_text.setWordWrap(True)
        impact_text.setStyleSheet("font-size: 17px; color: #000000; line-height: 1.6;")
        impact_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        impact_layout.addWidget(impact_title)
        impact_layout.addWidget(impact_text)
        
        layout.addWidget(impact_frame)
        
        return container

    def create_buttons(self):
        layout = QHBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        back_button = ModernButton(
            text="Volver al Inicio",
            button_type="secondary",
            icon_text="🏠"
        )
        back_button.setFixedSize(220, 55)
        back_button.clicked.connect(self.volver_inicio)
        layout.addWidget(back_button)
        
        return layout

    def volver_inicio(self):
        if self.parent_app:
            self.parent_app.show()
        self.close()