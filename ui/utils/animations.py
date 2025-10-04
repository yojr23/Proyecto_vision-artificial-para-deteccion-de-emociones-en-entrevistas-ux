from PySide6.QtWidgets import QLabel, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, QTimer
from PySide6.QtGui import QColor

class AnimatedLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity") 
        self.original_geometry = None
        self.is_animated = False
        
    def setOriginalGeometry(self, rect):
        self.original_geometry = rect
        
    def startBounceAnimation(self):
        if not self.original_geometry or self.is_animated:
            return
            
        self.is_animated = True
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        
        # Animación de rebote hacia arriba
        bounce_rect = QRect(
            self.original_geometry.x(),
            self.original_geometry.y() - 20,
            self.original_geometry.width(),
            self.original_geometry.height()
        )
        
        self.animation.setStartValue(self.original_geometry)
        self.animation.setEndValue(bounce_rect)
        self.animation.finished.connect(self.returnToOriginal)
        self.animation.start()
        
    def returnToOriginal(self):
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.original_geometry)
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.finished.connect(self.resetAnimation)
        self.animation.start()
        
    def resetAnimation(self):
        self.is_animated = False

class TitleAnimator:
    """Clase para manejar animaciones del título principal"""
    
    @staticmethod
    def setupTitleShadow(title_widget):
        """Configurar sombra para el título"""
        title_shadow = QGraphicsDropShadowEffect()
        title_shadow.setBlurRadius(15)
        title_shadow.setColor(QColor(34, 139, 34, 120))
        title_shadow.setOffset(3, 3)
        title_widget.setGraphicsEffect(title_shadow)
    
    @staticmethod
    def createTitleStyle():
        """Retornar el estilo CSS para el título principal"""
        return """
            QLabel {
                font-size: 64px;
                font-weight: 900;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                            stop:0 #228B22, stop:0.3 #32CD32, 
                            stop:0.7 #00FF00, stop:1 #006400);
                -webkit-background-clip: text;
                color: transparent;
                letter-spacing: 4px;
                text-shadow: 2px 2px 4px rgba(34, 139, 34, 0.3);
            }
        """

class ButtonAnimator:
    """Clase para manejar animaciones de botones"""
    
    @staticmethod
    def setupButtonAnimation(button):
        """Configurar animaciones para un botón"""
        button.scale_animation = QPropertyAnimation(button, b"geometry")
        button.scale_animation.setDuration(150)
        button.scale_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    @staticmethod
    def animateScale(button, scale_factor):
        """Animar escala de un botón"""
        if not hasattr(button, 'scale_animation'):
            ButtonAnimator.setupButtonAnimation(button)
            
        current_geometry = button.geometry()
        center = current_geometry.center()
        
        new_width = int(button.width() * scale_factor)
        new_height = int(button.height() * scale_factor)
        
        new_geometry = QRect(
            center.x() - new_width // 2,
            center.y() - new_height // 2,
            new_width,
            new_height
        )
        
        button.scale_animation.setStartValue(current_geometry)
        button.scale_animation.setEndValue(new_geometry)
        button.scale_animation.start()

class FloatingAnimator:
    """Clase para manejar animaciones flotantes"""
    
    @staticmethod
    def setupFloatingAnimation(widget, duration=2000):
        """Configurar animación flotante para un widget"""
        widget.float_animation = QPropertyAnimation(widget, b"geometry")
        widget.float_animation.setDuration(duration)
        widget.float_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        widget.float_animation.setLoopCount(-1)  # Infinito
        
        # Timer para iniciar animación flotante
        QTimer.singleShot(1000, lambda: FloatingAnimator.startFloating(widget))
    
    @staticmethod
    def startFloating(widget):
        """Iniciar animación flotante"""
        if not hasattr(widget, 'float_animation') or not widget.geometry().isValid():
            return
            
        current_geometry = widget.geometry()
        float_geometry = QRect(
            current_geometry.x(),
            current_geometry.y() - 10,
            current_geometry.width(),
            current_geometry.height()
        )
        
        widget.float_animation.setStartValue(current_geometry)
        widget.float_animation.setEndValue(float_geometry)
        widget.float_animation.start()

class IconAnimator:
    """Clase para manejar animaciones de iconos"""
    
    @staticmethod
    def setupIconHoverAnimation(icon_widget, scale_factor=1.1):
        """Configurar animación hover para iconos"""
        def on_enter():
            IconAnimator.scaleIcon(icon_widget, scale_factor)
            
        def on_leave():
            IconAnimator.scaleIcon(icon_widget, 1.0)
            
        # Almacenar referencias para evitar garbage collection
        icon_widget._enter_callback = on_enter
        icon_widget._leave_callback = on_leave
        
        return on_enter, on_leave
    
    @staticmethod
    def scaleIcon(icon_widget, scale_factor):
        """Escalar icono con animación"""
        if not hasattr(icon_widget, 'icon_animation'):
            icon_widget.icon_animation = QPropertyAnimation(icon_widget, b"geometry")
            icon_widget.icon_animation.setDuration(200)
            icon_widget.icon_animation.setEasingCurve(QEasingCurve.Type.OutBack)
        
        current = icon_widget.geometry()
        center = current.center()
        
        new_width = int(current.width() * scale_factor)
        new_height = int(current.height() * scale_factor)
        
        scaled = QRect(
            center.x() - new_width // 2,
            center.y() - new_height // 2,
            new_width,
            new_height
        )
        
        icon_widget.icon_animation.setStartValue(current)
        icon_widget.icon_animation.setEndValue(scaled)
        icon_widget.icon_animation.start()