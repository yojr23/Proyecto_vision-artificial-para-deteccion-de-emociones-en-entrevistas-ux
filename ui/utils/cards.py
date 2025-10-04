from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QRect
from PySide6.QtGui import QColor
from .animations import FloatingAnimator, IconAnimator

class FloatingCard(QFrame):
    """Tarjeta flotante con animaciones y efectos visuales"""
    
    def __init__(self, title, description, icon="🌱", color_theme="green"):
        super().__init__()
        self.color_theme = color_theme
        self.setupCard()
        self.createContent(title, description, icon)
        self.setupAnimations()
        self.setupShadow()
        
    def setupCard(self):
        """Configuración básica de la tarjeta"""
        self.setFixedSize(350, 220)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setStyleSheet(self.getCardStyle())
        
    def createContent(self, title, description, icon):
        """Crear el contenido de la tarjeta"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icono animado
        self.icon_label = self.createIconLabel(icon)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Título
        title_label = self.createTitleLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Descripción
        desc_label = self.createDescriptionLabel(description)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        
    def createIconLabel(self, icon):
        """Crear etiqueta de icono con estilo"""
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 48px;
                color: #228B22;
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.8,
                            stop:0 rgba(50, 205, 50, 0.2), stop:1 rgba(144, 238, 144, 0.1));
                border-radius: 45px;
                min-height: 90px;
                max-height: 90px;
                border: 2px solid rgba(34, 139, 34, 0.3);
            }}
        """)
        return icon_label
        
    def createTitleLabel(self, title):
        """Crear etiqueta de título"""
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #006400;
                margin: 8px 0;
                letter-spacing: 1px;
            }
        """)
        return title_label
        
    def createDescriptionLabel(self, description):
        """Crear etiqueta de descripción"""
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #2F4F2F;
                line-height: 1.5;
            }
        """)
        return desc_label
    
    def getCardStyle(self):
        """Obtener estilo CSS de la tarjeta"""
        return """
            FloatingCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 #FFFFFF, stop:0.5 #FAFFFE, stop:1 #F0FFF0);
                border-radius: 20px;
                border: 2px solid rgba(50, 205, 50, 0.3);
            }
        """
    
    def setupAnimations(self):
        """Configurar animaciones de la tarjeta"""
        FloatingAnimator.setupFloatingAnimation(self, duration=2000)
        
    def setupShadow(self):
        """Configurar sombra de la tarjeta"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)
        
    def enterEvent(self, event):
        """Evento al pasar el mouse por encima"""
        IconAnimator.scaleIcon(self.icon_label, 1.1)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Evento al salir el mouse"""
        IconAnimator.scaleIcon(self.icon_label, 1.0)
        super().leaveEvent(event)

class InfoCard(QFrame):
    """Tarjeta de información con panel expandido"""
    
    def __init__(self, width=600):
        super().__init__()
        self.setupInfoCard(width)
        self.createInfoContent()
        self.setupInfoShadow()
    
    def setupInfoCard(self, width):
        """Configuración básica de la tarjeta de información"""
        self.setFixedWidth(width)
        self.setStyleSheet(self.getInfoStyle())
        
    def createInfoContent(self):
        """Crear contenido de información"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Título
        title = self.createInfoTitle()
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Descripción detallada
        description = self.createInfoDescription()
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description, alignment=Qt.AlignmentFlag.AlignHCenter)
        
    def createInfoTitle(self):
        """Crear título de información"""
        title = QLabel("🌾 Sobre AGRIOT")
        title.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: 700;
                color: #006400;
                padding-bottom: 15px;
                letter-spacing: 2px;
            }
        """)
        return title
        
    def createInfoDescription(self):
        """Crear descripción detallada"""
        description = QLabel(self.getInfoText())
        description.setWordWrap(True)
        description.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #2F4F2F;
                line-height: 1.7;
                padding: 25px;
                background: rgba(240, 255, 240, 0.5);
                border-radius: 20px;
                border-left: 5px solid #32CD32;
            }
        """)
        return description
        
    def getInfoText(self):
        """Obtener texto de información"""
        return """
        <b>AGRIOT</b> es el semillero de investigación más innovador en experiencia de usuario agrícola. 
        Utilizamos inteligencia artificial de vanguardia para detectar emociones durante las interacciones 
        con tecnologías digitales, creando soluciones verdaderamente inclusivas.
        
        <br><br><b>🎯 Características Principales:</b>
        <br>• Detección automática de emociones en tiempo real
        <br>• Análisis contextualizado para entornos rurales  
        <br>• Reportes visuales interactivos y detallados
        <br>• Metodología centrada en el empoderamiento femenino
        
        <br><br><b>🌍 Impacto Social:</b>
        <br>Enfocado en la vereda Mancilla, Los Santos, Santander, como parte del proyecto 
        <i>"Sembrando Bits: Empoderando a la mujer agricultora"</i>, transformando vidas 
        a través de la tecnología accesible.
        """
        
    def getInfoStyle(self):
        """Obtener estilo CSS de la tarjeta de información"""
        return """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                            stop:0 rgba(255, 255, 255, 0.9), 
                            stop:1 rgba(240, 255, 240, 0.9));
                border-radius: 25px;
                border: 2px solid rgba(50, 205, 50, 0.3);
            }
        """
        
    def setupInfoShadow(self):
        """Configurar sombra de la tarjeta de información"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)

class MascotCard(QFrame):
    """Tarjeta contenedora de la mascota con animaciones"""
    
    def __init__(self, size=380):
        super().__init__()
        self.setupMascotCard(size)
        self.setupMascotShadow()
        
    def setupMascotCard(self, size):
        """Configuración de la tarjeta de mascota"""
        self.setFixedSize(size, size)
        self.setStyleSheet(self.getMascotStyle(size // 2))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def getMascotStyle(self, border_radius):
        """Obtener estilo CSS de la tarjeta de mascota (más verde y consistente)"""
        return f"""
            QFrame {{
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.7,
                            stop:0 #E0FFE0, stop:0.7 #B8FFB8, stop:1 #32CD32);
                border: 4px solid #32CD32;
                border-radius: {border_radius}px;
            }}
        """
        
    def setupMascotShadow(self):
        """Configurar sombra de la tarjeta de mascota"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(20)
        shadow.setColor(QColor(34, 139, 34, 60))
        self.setGraphicsEffect(shadow)