from PySide6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
from PySide6.QtGui import QColor
from .animations import ButtonAnimator

class ModernButton(QPushButton):
    """Botón moderno con animaciones y estilos avanzados"""
    
    def __init__(self, text, button_type="primary", icon_text="", parent=None):
        super().__init__(parent)
        self.button_type = button_type
        self.icon_text = icon_text
        self.setText(f"{icon_text} {text}" if icon_text else text)
        
        self.setupButton()
        self.setupAnimations()
        self.setupShadow()
        self.setStyleSheet(self.getButtonStyle())
    
    def setupButton(self):
        """Configuración básica del botón"""
        self.setFixedHeight(70)
        self.setFixedWidth(320)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def setupAnimations(self):
        """Configurar animaciones del botón"""
        ButtonAnimator.setupButtonAnimation(self)
        
    def setupShadow(self):
        """Configurar sombra del botón"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(34, 139, 34, 100))
        self.setGraphicsEffect(shadow)
    
    def getButtonStyle(self):
        """Obtener estilo CSS según el tipo de botón"""
        if self.button_type == "primary":
            return self.getPrimaryStyle()
        else:
            return self.getSecondaryStyle()
    
    def getPrimaryStyle(self):
        """Estilo para botón primario"""
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                            stop:0 #32CD32, stop:0.3 #228B22, stop:0.7 #006400, stop:1 #8FBC8F);
                color: white;
                font-size: 18px;
                font-weight: 700;
                border: none;
                border-radius: 35px;
                text-align: center;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                            stop:0 #3CB371, stop:0.3 #2E8B57, stop:0.7 #228B22, stop:1 #98FB98);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                            stop:0 #228B22, stop:0.3 #006400, stop:0.7 #2F4F2F, stop:1 #6B8E23);
            }
        """
    
    def getSecondaryStyle(self):
        """Estilo para botón secundario"""
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                            stop:0 #F0FFF0, stop:1 #E6FFE6);
                color: #006400;
                font-size: 18px;
                font-weight: 600;
                border: 3px solid #32CD32;
                border-radius: 35px;
                text-align: center;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                            stop:0 #98FB98, stop:1 #90EE90);
                border: 3px solid #228B22;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                            stop:0 #90EE90, stop:1 #98FB98);
                border: 3px solid #006400;
            }
        """
        
    def enterEvent(self, event):
        """Evento al pasar el mouse (sin animación de escala)"""
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Evento al salir el mouse (sin animación de escala)"""
        super().leaveEvent(event)

class IconButton(QPushButton):
    """Botón con icono prominente"""
    
    def __init__(self, text, icon, parent=None):
        super().__init__(parent)
        self.setText(f"{icon}\n{text}")
        self.setupIconButton()
        
    def setupIconButton(self):
        """Configuración del botón con icono"""
        self.setFixedSize(120, 120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(self.getIconButtonStyle())
        
        # Sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(34, 139, 34, 80))
        self.setGraphicsEffect(shadow)
    
    def getIconButtonStyle(self):
        """Estilo para botón con icono"""
        return """
            QPushButton {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.8,
                            stop:0 #FFFFFF, stop:1 #F0FFF0);
                color: #228B22;
                font-size: 12px;
                font-weight: 600;
                border: 2px solid #32CD32;
                border-radius: 60px;
                text-align: center;
                line-height: 1.2;
            }
            QPushButton:hover {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.8,
                            stop:0 #F0FFF0, stop:1 #E0FFE0);
                border: 2px solid #228B22;
            }
            QPushButton:pressed {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.8,
                            stop:0 #E0FFE0, stop:1 #D0FFD0);
                border: 2px solid #006400;
            }
        """

class FloatingActionButton(QPushButton):
    """Botón de acción flotante estilo Material Design"""
    
    def __init__(self, icon, parent=None):
        super().__init__(icon, parent)
        self.setupFAB()
        
    def setupFAB(self):
        """Configuración del FAB"""
        self.setFixedSize(80, 80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(self.getFABStyle())
        
        # Sombra prominente
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(15)
        shadow.setColor(QColor(34, 139, 34, 100))
        self.setGraphicsEffect(shadow)
        
        # Animación de scale
        self.scale_animation = QPropertyAnimation(self, b"geometry")
        self.scale_animation.setDuration(200)
        self.scale_animation.setEasingCurve(QEasingCurve.Type.OutBack)
        
    def getFABStyle(self):
        """Estilo para FAB"""
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                            stop:0 #32CD32, stop:1 #228B22);
                color: white;
                font-size: 28px;
                font-weight: bold;
                border: none;
                border-radius: 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                            stop:0 #3CB371, stop:1 #2E8B57);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                            stop:0 #228B22, stop:1 #006400);
            }
        """
        
    def enterEvent(self, event):
        """Animación al hover"""
        current = self.geometry()
        scaled = QRect(
            current.x() - 5, current.y() - 5, 
            current.width() + 10, current.height() + 10
        )
        
        self.scale_animation.setStartValue(current)
        self.scale_animation.setEndValue(scaled)
        self.scale_animation.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Volver al tamaño normal"""
        self.scale_animation.setDirection(QPropertyAnimation.Direction.Backward)
        self.scale_animation.start()
        super().leaveEvent(event)