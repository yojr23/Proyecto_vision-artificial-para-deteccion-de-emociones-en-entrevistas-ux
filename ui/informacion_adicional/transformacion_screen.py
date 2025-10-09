from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpacerItem, QSizePolicy, QPushButton, QScrollArea, QFrame, QGridLayout
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
        scroll_layout.setSpacing(40)
        scroll_layout.setContentsMargins(60, 50, 60, 50)

        # Header
        scroll_layout.addLayout(self.create_header())

        # Banner de visión
        scroll_layout.addWidget(self.create_vision_banner())

        # Contexto y brechas
        scroll_layout.addWidget(self.create_context_section())

        # Programas de empoderamiento
        scroll_layout.addWidget(self.create_programs_section())

        # Impacto y métricas
        scroll_layout.addWidget(self.create_impact_section())

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

        icon = QLabel("🚀")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 90px;")
        layout.addWidget(icon)

        title = QLabel("Transformación Digital Rural")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 52px; 
            font-weight: bold; 
            color: #000000;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)

        subtitle = QLabel(
            "Empoderando a mujeres campesinas mediante tecnología accesible, "
            "intuitiva y adaptada a las necesidades del campo colombiano"
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

    def create_vision_banner(self):
        """Banner destacado con la visión del proyecto"""
        banner = QFrame()
        banner.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 215, 0, 0.3),
                    stop:0.5 rgba(255, 165, 0, 0.25),
                    stop:1 rgba(255, 140, 0, 0.2));
                border: 3px solid rgba(255, 165, 0, 0.5);
                border-radius: 20px;
                padding: 30px;
            }
        """)
        
        layout = QHBoxLayout(banner)
        layout.setSpacing(20)
        
        # Icono grande
        icon_label = QLabel("💡")
        icon_label.setStyleSheet("font-size: 70px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Contenido
        content_layout = QVBoxLayout()
        content_layout.setSpacing(10)
        
        vision_title = QLabel("Nuestra Visión")
        vision_title.setStyleSheet("font-size: 26px; font-weight: bold; color: #000000;")
        
        vision_text = QLabel(
            "Cerrar la brecha digital de género en zonas rurales de Los Santos, "
            "transformando la vida de las mujeres campesinas a través de la alfabetización "
            "digital y el acceso equitativo a tecnologías agrícolas innovadoras que impulsen "
            "su desarrollo personal, económico y comunitario."
        )
        vision_text.setWordWrap(True)
        vision_text.setStyleSheet("font-size: 18px; color: #000000; line-height: 1.6;")
        
        content_layout.addWidget(vision_title)
        content_layout.addWidget(vision_text)
        
        layout.addWidget(icon_label)
        layout.addLayout(content_layout, 1)
        
        return banner

    def create_context_section(self):
        """Sección de contexto con línea de tiempo vertical"""
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
        section_title = QLabel("📊 Diagnóstico Actual de Los Santos")
        section_title.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold; 
            color: #000000;
            margin-bottom: 10px;
        """)
        section_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(section_title)
        
        # Timeline vertical
        timeline_data = [
            ("🌎", "Población", "15,503 habitantes", "48.7% mujeres", "rgba(100, 181, 246, 0.2)"),
            ("📱", "Conectividad", "Solo 40% acceso a internet", "Brecha digital crítica", "rgba(255, 167, 38, 0.2)"),
            ("👩‍🌾", "Participación", "Mujeres líderes agrícolas", "Toma de decisiones activa", "rgba(129, 199, 132, 0.2)"),
            ("⚠️", "Desafíos", "Baja alfabetización digital", "Acceso limitado a tecnología", "rgba(239, 83, 80, 0.2)")
        ]
        
        for icon, title, stat1, stat2, color in timeline_data:
            timeline_item = self.create_timeline_item(icon, title, stat1, stat2, color)
            layout.addWidget(timeline_item)
        
        return container

    def create_timeline_item(self, icon, title, stat1, stat2, color):
        """Crea un item de línea de tiempo"""
        item = QFrame()
        item.setStyleSheet(f"""
            QFrame {{
                background: {color};
                border-left: 5px solid rgba(34, 139, 34, 0.6);
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        
        layout = QHBoxLayout(item)
        layout.setSpacing(20)
        
        # Icono
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 50px;")
        icon_label.setFixedWidth(70)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Contenido
        content_layout = QVBoxLayout()
        content_layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #000000;")
        
        stat1_label = QLabel(f"• {stat1}")
        stat1_label.setStyleSheet("font-size: 17px; color: #000000;")
        
        stat2_label = QLabel(f"• {stat2}")
        stat2_label.setStyleSheet("font-size: 17px; color: #000000;")
        
        content_layout.addWidget(title_label)
        content_layout.addWidget(stat1_label)
        content_layout.addWidget(stat2_label)
        
        layout.addWidget(icon_label)
        layout.addLayout(content_layout, 1)
        
        return item

    def create_programs_section(self):
        """Sección de programas con diseño de cards interactivas"""
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
        section_title = QLabel("🛠️ Programas de Empoderamiento Digital")
        section_title.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold; 
            color: #000000;
            margin-bottom: 10px;
        """)
        section_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(section_title)
        
        # Descripción
        desc = QLabel(
            "Iniciativas especializadas diseñadas para fortalecer las capacidades digitales "
            "y el empoderamiento tecnológico de las mujeres campesinas"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 18px; color: #000000; margin-bottom: 15px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Grid 3x2 de programas
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        
        programs = [
            ("💻", "Capacitación Digital", "Formación en herramientas digitales agrícolas esenciales", "#e8f5e9"),
            ("🎯", "Mentoría Tecnológica", "Acompañamiento en emprendimiento tecnológico rural", "#e3f2fd"),
            ("🛒", "Comercialización Digital", "Acceso a plataformas de venta online y marketplace", "#fff3e0"),
            ("📊", "Análisis de Datos", "Formación en interpretación de datos para agricultura", "#f3e5f5"),
            ("🤝", "Redes de Innovación", "Comunidades de mujeres innovadoras del sector", "#fce4ec"),
            ("📱", "Apps Agrícolas", "Uso de aplicaciones móviles para gestión de cultivos", "#e0f2f1")
        ]
        
        for i, (icon, title, description, color) in enumerate(programs):
            row = i // 2
            col = i % 2
            
            program_card = QFrame()
            program_card.setStyleSheet(f"""
                QFrame {{
                    background: {color};
                    border: 2px solid rgba(34, 139, 34, 0.3);
                    border-radius: 15px;
                    padding: 20px;
                }}
                QFrame:hover {{
                    border: 3px solid rgba(34, 139, 34, 0.6);
                    background: {color};
                }}
            """)
            
            card_layout = QVBoxLayout(program_card)
            card_layout.setSpacing(10)
            
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 45px;")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            title_label = QLabel(title)
            title_label.setStyleSheet("font-size: 19px; font-weight: bold; color: #000000;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("font-size: 15px; color: #000000; line-height: 1.4;")
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            card_layout.addWidget(icon_label)
            card_layout.addWidget(title_label)
            card_layout.addWidget(desc_label)
            
            grid_layout.addWidget(program_card, row, col)
        
        layout.addLayout(grid_layout)
        
        return container

    def create_impact_section(self):
        """Sección de impacto con métricas destacadas"""
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
        section_title = QLabel("📈 Impacto y Resultados Proyectados")
        section_title.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold; 
            color: #000000;
            margin-bottom: 10px;
        """)
        section_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(section_title)
        
        # Métricas principales - grid horizontal
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15)
        
        metrics = [
            ("👥", "500+", "Mujeres Capacitadas", "rgba(76, 175, 80, 0.2)"),
            ("📱", "85%", "Adopción Tecnológica", "rgba(33, 150, 243, 0.2)"),
            ("📊", "60%", "Mejora en Productividad", "rgba(255, 152, 0, 0.2)"),
            ("🚀", "25", "Emprendimientos Creados", "rgba(156, 39, 176, 0.2)")
        ]
        
        for icon, number, label, color in metrics:
            metric_card = QFrame()
            metric_card.setStyleSheet(f"""
                QFrame {{
                    background: {color};
                    border: 3px solid rgba(34, 139, 34, 0.4);
                    border-radius: 15px;
                    padding: 25px 20px;
                }}
            """)
            
            metric_layout = QVBoxLayout(metric_card)
            metric_layout.setSpacing(8)
            
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 40px;")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            number_label = QLabel(number)
            number_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #000000;")
            number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            label_label = QLabel(label)
            label_label.setWordWrap(True)
            label_label.setStyleSheet("font-size: 16px; color: #000000; font-weight: bold;")
            label_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            metric_layout.addWidget(icon_label)
            metric_layout.addWidget(number_label)
            metric_layout.addWidget(label_label)
            
            metrics_layout.addWidget(metric_card)
        
        layout.addLayout(metrics_layout)
        
        # Beneficios adicionales
        benefits_frame = QFrame()
        benefits_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(144, 238, 144, 0.3),
                    stop:1 rgba(34, 139, 34, 0.2));
                border: 2px solid rgba(34, 139, 34, 0.4);
                border-radius: 15px;
                padding: 25px;
                margin-top: 15px;
            }
        """)
        
        benefits_layout = QVBoxLayout(benefits_frame)
        benefits_layout.setSpacing(12)
        
        benefits_title = QLabel("🎯 Beneficios Clave del Proyecto")
        benefits_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #000000;")
        benefits_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        benefits_layout.addWidget(benefits_title)
        
        benefits = [
            "✅ Reducción de la brecha digital de género en 40%",
            "✅ Aumento de ingresos económicos de mujeres campesinas",
            "✅ Fortalecimiento de la autonomía y toma de decisiones",
            "✅ Acceso equitativo a información y recursos digitales",
            "✅ Creación de comunidades digitales de apoyo mutuo"
        ]
        
        for benefit in benefits:
            benefit_label = QLabel(benefit)
            benefit_label.setStyleSheet("font-size: 17px; color: #000000; padding: 3px 0;")
            benefits_layout.addWidget(benefit_label)
        
        layout.addWidget(benefits_frame)
        
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