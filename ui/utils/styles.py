"""
Utilidades de estilos CSS para la aplicación AGRIOT
Contiene paletas de colores, estilos comunes y temas
"""

class ColorPalette:
    """Paleta de colores para el tema AGRIOT"""
    
    # Verdes primarios
    PRIMARY_GREEN = "#32CD32"      # Lime Green
    DARK_GREEN = "#228B22"         # Forest Green  
    DEEP_GREEN = "#006400"         # Dark Green
    SAGE_GREEN = "#8FBC8F"         # Dark Sea Green
    
    # Verdes secundarios
    LIGHT_GREEN = "#90EE90"        # Light Green
    PALE_GREEN = "#98FB98"         # Pale Green
    MINT_GREEN = "#F0FFF0"         # Honeydew
    VERY_LIGHT_GREEN = "#E6FFE6"   # Very Light Green
    
    # Verdes de acento
    SEA_GREEN = "#3CB371"          # Medium Sea Green
    SPRING_GREEN = "#2E8B57"       # Sea Green
    OLIVE_GREEN = "#6B8E23"        # Olive Drab
    DARK_OLIVE = "#2F4F2F"         # Dark Slate Gray
    
    # Colores de apoyo
    WHITE = "#FFFFFF"
    OFF_WHITE = "#FAFFFE"
    LIGHT_GRAY = "#F8F8F8"
    TRANSPARENT_GREEN = "rgba(50, 205, 50, 0.1)"

class GradientStyles:
    """Estilos de gradientes predefinidos"""
    
    @staticmethod
    def primary_gradient():
        """Gradiente principal verde"""
        return """qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                  stop:0 #32CD32, stop:0.3 #228B22, 
                  stop:0.7 #006400, stop:1 #8FBC8F)"""
    
    @staticmethod
    def background_gradient():
        """Gradiente para fondo principal"""
        return """qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                  stop:0 #E0FFE0, stop:0.25 #F0FFF0, 
                  stop:0.5 #E6FFE6, stop:0.75 #CCFFCC, stop:1 #B8FFB8)"""
    
    @staticmethod
    def card_gradient():
        """Gradiente para tarjetas"""
        return """qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                  stop:0 #FFFFFF, stop:0.5 #FAFFFE, stop:1 #F0FFF0)"""
    
    @staticmethod
    def title_gradient():
        """Gradiente para títulos"""
        return """qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                  stop:0 #228B22, stop:0.3 #32CD32, 
                  stop:0.7 #00FF00, stop:1 #006400)"""
    
    @staticmethod
    def radial_gradient():
        """Gradiente radial para elementos circulares"""
        return """qradialgradient(cx:0.5, cy:0.5, radius:0.8,
                  stop:0 rgba(50, 205, 50, 0.2), stop:1 rgba(144, 238, 144, 0.1))"""

class CommonStyles:
    """Estilos comunes reutilizables"""
    
    @staticmethod
    def modern_frame():
        """Estilo para frame moderno"""
        return f"""
            QFrame {{
                background: {GradientStyles.card_gradient()};
                border-radius: 20px;
                border: 2px solid {ColorPalette.TRANSPARENT_GREEN};
            }}
        """
    
    @staticmethod
    def title_style(font_size=32):
        """Estilo para títulos"""
        return f"""
            QLabel {{
                font-size: {font_size}px;
                font-weight: 700;
                color: {ColorPalette.DEEP_GREEN};
                letter-spacing: 2px;
            }}
        """
    
    @staticmethod
    def subtitle_style(font_size=18):
        """Estilo para subtítulos"""
        return f"""
            QLabel {{
                font-size: {font_size}px;
                color: {ColorPalette.DARK_OLIVE};
                font-style: italic;
                letter-spacing: 1px;
            }}
        """
    
    @staticmethod
    def description_style():
        """Estilo para texto descriptivo"""
        return f"""
            QLabel {{
                font-size: 16px;
                color: {ColorPalette.DARK_OLIVE};
                line-height: 1.7;
                padding: 25px;
                background: {ColorPalette.TRANSPARENT_GREEN};
                border-radius: 20px;
                border-left: 5px solid {ColorPalette.PRIMARY_GREEN};
            }}
        """

class ShadowEffects:
    """Configuraciones de efectos de sombra"""
    
    @staticmethod
    def get_drop_shadow(blur=20, offset_x=0, offset_y=8, color=(0, 0, 0, 30)):
        """Crear efecto de sombra básico"""
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        from PySide6.QtGui import QColor
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setXOffset(offset_x)
        shadow.setYOffset(offset_y)
        shadow.setColor(QColor(*color))
        return shadow
    
    @staticmethod
    def get_green_shadow(blur=25, offset_y=10, opacity=100):
        """Crear sombra verde para elementos destacados"""
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        from PySide6.QtGui import QColor
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setXOffset(0)
        shadow.setYOffset(offset_y)
        shadow.setColor(QColor(34, 139, 34, opacity))
        return shadow

class AnimationSettings:
    """Configuraciones para animaciones"""
    
    # Duraciones estándar
    FAST_DURATION = 150
    MEDIUM_DURATION = 300
    SLOW_DURATION = 500
    VERY_SLOW_DURATION = 1000
    
    # Factores de escala
    HOVER_SCALE = 1.05
    CLICK_SCALE = 0.95
    ICON_SCALE = 1.1
    
    # Desplazamientos
    BOUNCE_OFFSET = 20
    FLOAT_OFFSET = 10

class MessageBoxStyles:
    """Estilos para cuadros de mensaje"""
    
    @staticmethod
    def get_modern_messagebox_style():
        """Estilo moderno para MessageBox"""
        return f"""
            QMessageBox {{
                background: {GradientStyles.card_gradient()};
                border-radius: 15px;
                border: 2px solid {ColorPalette.TRANSPARENT_GREEN};
            }}
            QMessageBox QPushButton {{
                background: {GradientStyles.primary_gradient()};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }}
            QMessageBox QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                            stop:0 #228B22, stop:1 #006400);
            }}
            QMessageBox QLabel {{
                color: {ColorPalette.DARK_OLIVE};
                font-size: 14px;
                padding: 10px;
            }}
        """

class LayoutSettings:
    """Configuraciones de layout"""
    
    # Márgenes estándar
    SMALL_MARGIN = 15
    MEDIUM_MARGIN = 25
    LARGE_MARGIN = 40
    
    # Espaciados
    SMALL_SPACING = 10
    MEDIUM_SPACING = 20
    LARGE_SPACING = 30
    EXTRA_LARGE_SPACING = 40
    
    # Tamaños de componentes
    BUTTON_HEIGHT = 70
    BUTTON_WIDTH = 320
    CARD_WIDTH = 350
    CARD_HEIGHT = 220

class FontSettings:
    """Configuraciones de fuentes"""
    
    # Tamaños de fuente
    SMALL_FONT = 12
    MEDIUM_FONT = 16
    LARGE_FONT = 20
    TITLE_FONT = 32
    HEADER_FONT = 48
    LOGO_FONT = 64
    
    # Pesos de fuente
    LIGHT_WEIGHT = 300
    NORMAL_WEIGHT = 400
    MEDIUM_WEIGHT = 500
    SEMIBOLD_WEIGHT = 600
    BOLD_WEIGHT = 700
    BLACK_WEIGHT = 900