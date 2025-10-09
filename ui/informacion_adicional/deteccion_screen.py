from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpacerItem, QSizePolicy, QPushButton, QScrollArea, QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from ..utils.styles import ColorPalette, GradientStyles
from ..utils.buttons import ModernButton

class DeteccionScreen(QMainWindow):
    """Pantalla de Detección Emocional IA Mejorada"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.setup_window()
        self.setup_ui()
        
    def setup_window(self):
        self.setWindowTitle("AGRIOT - Detección Emocional IA")
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
        
        # Info resumida de contexto
        scroll_layout.addWidget(self.create_context_section())
        
        # Características IA
        scroll_layout.addWidget(self.create_features_section())
        
        # Beneficios y Metodología lado a lado
        scroll_layout.addLayout(self.create_benefits_methodology_section())
        
        # Resultados y Presupuesto
        scroll_layout.addLayout(self.create_results_budget_section())
        
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
        
        icon = QLabel("🤖")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 90px;")
        layout.addWidget(icon)
        
        title = QLabel("Detección Emocional IA")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 52px; 
            font-weight: bold; 
            color: #000000;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        subtitle = QLabel(
            "Analizando emociones de mujeres campesinas en pruebas UX "
            "mediante visión artificial y metodología Doble Diamante"
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
        """Sección de contexto con cards mejoradas"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 25px;
                padding: 30px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        
        # Título de sección
        section_title = QLabel("📊 Contexto del Proyecto")
        section_title.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold; 
            color: #000000;
            margin-bottom: 10px;
        """)
        section_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(section_title)
        
        # Grid de cards
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        
        cards_info = [
            ("🌎", "Población Rural", "Los Santos: 15,503 habitantes\n48.7% mujeres (DANE 2024)"),
            ("📱", "Brecha Digital", "Solo 40% con acceso a internet\nen zonas rurales"),
            ("👩‍🌾", "Rol de la Mujer", "Participación activa en agricultura\ny decisiones locales"),
            ("⚠️", "Desafíos Clave", "Baja alfabetización digital\nAcceso limitado a tecnología")
        ]
        
        for i, (icon, title, text) in enumerate(cards_info):
            row = i // 2
            col = i % 2
            card = self.create_info_card(icon, title, text)
            grid_layout.addWidget(card, row, col)
        
        layout.addLayout(grid_layout)
        return container
    
    def create_info_card(self, icon, title, text):
        """Crea una card de información individual"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(144, 238, 144, 0.3),
                    stop:1 rgba(34, 139, 34, 0.2));
                border: 2px solid rgba(34, 139, 34, 0.3);
                border-radius: 15px;
                padding: 20px;
            }
            QFrame:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(144, 238, 144, 0.4),
                    stop:1 rgba(34, 139, 34, 0.3));
                border: 2px solid rgba(34, 139, 34, 0.5);
            }
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)
        
        lbl_icon = QLabel(icon)
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setStyleSheet("font-size: 48px;")
        
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
    
    def create_features_section(self):
        """Sección de características IA"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 25px;
                padding: 30px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        
        title = QLabel("✨ Características de la IA")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #000000;")
        layout.addWidget(title)
        
        features = [
            "🎯 Reconocimiento facial y detección de microexpresiones en tiempo real",
            "😊 Detección de emociones: felicidad, tristeza, enojo y neutral",
            "⚡ Análisis en tiempo real o por segmentos de video pregrabado",
            "📷 Integración con cámaras RGB de bajo costo accesibles",
            "🔧 Algoritmos optimizados para contextos rurales colombianos"
        ]
        
        for text in features:
            text_label = QLabel(text)
            text_label.setWordWrap(True)
            text_label.setStyleSheet("font-size: 18px; color: #000000; padding: 5px 0;")
            layout.addWidget(text_label)
            
            layout.addLayout(layout)
        
        return container
    
    def create_benefits_methodology_section(self):
        """Beneficios y Metodología lado a lado"""
        layout = QHBoxLayout()
        layout.setSpacing(25)
        
        # Beneficios UX
        benefits_container = QFrame()
        benefits_container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 25px;
                padding: 30px;
            }
        """)
        
        benefits_layout = QVBoxLayout(benefits_container)
        benefits_layout.setSpacing(15)
        
        benefits_title = QLabel("🌟 Beneficios UX")
        benefits_title.setStyleSheet("font-size: 28px; font-weight: bold; color: #000000;")
        benefits_layout.addWidget(benefits_title)
        
        benefits = [
            ("📊", "Evaluación objetiva de experiencia de usuaria"),
            ("🔍", "Identificación de frustraciones y confusiones"),
            ("⚙️", "Optimización de interfaces digitales agrícolas"),
            ("👥", "Mayor inclusión de mujeres en diseño tecnológico"),
            ("🌐", "Reducción de la brecha digital rural")
        ]
        
        for icon, text in benefits:
            benefit_layout = QHBoxLayout()
            benefit_layout.setSpacing(10)
            
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 28px;")
            icon_label.setMinimumWidth(45)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            
            text_label = QLabel(text)
            text_label.setWordWrap(True)
            text_label.setStyleSheet("font-size: 16px; color: #000000;")
            
            benefit_layout.addWidget(icon_label)
            benefit_layout.addWidget(text_label)
            
            benefits_layout.addLayout(benefit_layout)
        
        # Metodología
        methodology_container = QFrame()
        methodology_container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 25px;
                padding: 30px;
            }
        """)
        
        methodology_layout = QVBoxLayout(methodology_container)
        methodology_layout.setSpacing(15)
        
        methodology_title = QLabel("📐 Metodología Doble Diamante")
        methodology_title.setStyleSheet("font-size: 28px; font-weight: bold; color: #000000;")
        methodology_layout.addWidget(methodology_title)
        
        phases = [
            ("1️⃣", "Descubrimiento", "Entrevistas y observación directa"),
            ("2️⃣", "Definición", "Análisis de emociones y necesidades"),
            ("3️⃣", "Desarrollo", "Diseño e implementación del prototipo"),
            ("4️⃣", "Entrega", "Validación y reporte de resultados")
        ]
        
        for icon, phase, desc in phases:
            phase_frame = QFrame()
            phase_frame.setStyleSheet("""
                QFrame {
                    background: rgba(34, 139, 34, 0.1);
                    border-left: 4px solid rgba(34, 139, 34, 0.6);
                    border-radius: 8px;
                    padding: 12px;
                }
            """)
            phase_layout = QVBoxLayout(phase_frame)
            phase_layout.setSpacing(5)
            
            phase_title = QLabel(f"{icon} {phase}")
            phase_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #000000;")
            
            phase_desc = QLabel(desc)
            phase_desc.setWordWrap(True)
            phase_desc.setStyleSheet("font-size: 15px; color: #000000;")
            
            phase_layout.addWidget(phase_title)
            phase_layout.addWidget(phase_desc)
            
            methodology_layout.addWidget(phase_frame)
        
        layout.addWidget(benefits_container)
        layout.addWidget(methodology_container)
        
        return layout
    
    def create_results_budget_section(self):
        """Resultados y Presupuesto lado a lado"""
        layout = QHBoxLayout()
        layout.setSpacing(25)
        
        # Resultados Esperados
        results_container = QFrame()
        results_container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 25px;
                padding: 30px;
            }
        """)
        
        results_layout = QVBoxLayout(results_container)
        results_layout.setSpacing(15)
        
        results_title = QLabel("🏆 Resultados Esperados")
        results_title.setStyleSheet("font-size: 28px; font-weight: bold; color: #000000;")
        results_layout.addWidget(results_title)
        
        results = [
            ("✅", "Prototipo funcional de visión artificial"),
            ("💾", "Base de datos anonimizada de imágenes faciales"),
            ("📄", "Informe técnico y validación de emociones"),
            ("📋", "Protocolo UX adaptado al contexto rural"),
            ("💡", "Recomendaciones de diseño para futuras apps")
        ]
        
        for icon, text in results:
            result_layout = QHBoxLayout()
            result_layout.setSpacing(10)
            
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 28px;")
            icon_label.setMinimumWidth(45)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            
            text_label = QLabel(text)
            text_label.setWordWrap(True)
            text_label.setStyleSheet("font-size: 16px; color: #000000;")
            
            result_layout.addWidget(icon_label)
            result_layout.addWidget(text_label)
            
            results_layout.addLayout(result_layout)
        
        # Presupuesto
        budget_container = QFrame()
        budget_container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 25px;
                padding: 30px;
            }
        """)
        
        budget_layout = QVBoxLayout(budget_container)
        budget_layout.setSpacing(15)
        
        budget_title = QLabel("💰 Presupuesto Resumido")
        budget_title.setStyleSheet("font-size: 28px; font-weight: bold; color: #000000;")
        budget_layout.addWidget(budget_title)
        
        budget_items = [
            ("🎥", "Hardware y Cámaras", "Equipos esenciales para pruebas en campo"),
            ("💻", "Software y Librerías", "OpenCV, TensorFlow, PySide6"),
            ("👨‍🏫", "Capacitación", "Formación y recursos humanos especializados"),
            ("📊", "Análisis de Datos", "Procesamiento y validación de resultados")
        ]
        
        for icon, category, desc in budget_items:
            budget_frame = QFrame()
            budget_frame.setStyleSheet("""
                QFrame {
                    background: rgba(255, 215, 0, 0.1);
                    border-left: 4px solid rgba(255, 165, 0, 0.6);
                    border-radius: 8px;
                    padding: 12px;
                }
            """)
            budget_item_layout = QVBoxLayout(budget_frame)
            budget_item_layout.setSpacing(5)
            
            item_title = QLabel(f"{icon} {category}")
            item_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #000000;")
            
            item_desc = QLabel(desc)
            item_desc.setWordWrap(True)
            item_desc.setStyleSheet("font-size: 15px; color: #000000;")
            
            budget_item_layout.addWidget(item_title)
            budget_item_layout.addWidget(item_desc)
            
            budget_layout.addWidget(budget_frame)
        
        layout.addWidget(results_container)
        layout.addWidget(budget_container)
        
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
        back_button.setFixedSize(220, 55)
        back_button.clicked.connect(self.volver_inicio)
        layout.addWidget(back_button)
        
        return layout
        
    def volver_inicio(self):
        if self.parent_app:
            self.parent_app.show()
        self.close()