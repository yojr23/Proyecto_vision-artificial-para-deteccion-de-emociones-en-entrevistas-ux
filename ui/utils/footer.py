from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class ModernFooter(QFrame):
    """Componente de footer moderno para la aplicación"""
    
    def __init__(self, height=100):
        super().__init__()
        self.setupFooter(height)
        self.createFooterContent()
        
    def setupFooter(self, height):
        """Configuración básica del footer"""
        self.setFixedHeight(height)
        self.setStyleSheet(self.getFooterStyle())
        
    def createFooterContent(self):
        """Crear contenido del footer"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)
        
        # Información del desarrollador
        developer_info = self.createDeveloperLabel()
        layout.addWidget(developer_info)
        
        # Información institucional
        institution_info = self.createInstitutionLabel()
        layout.addWidget(institution_info)
        
    def createDeveloperLabel(self):
        """Crear etiqueta con información del desarrollador"""
        developer_label = QLabel("Desarrollado por José Vicente Rincón Celis")
        developer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        developer_label.setStyleSheet(self.getDeveloperStyle())
        return developer_label
        
    def createInstitutionLabel(self):
        """Crear etiqueta con información institucional"""
        institution_label = QLabel("Universidad Autónoma de Bucaramanga • Semillero AGRIOT • 2025")
        institution_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        institution_label.setStyleSheet(self.getInstitutionStyle())
        return institution_label
        
    def getFooterStyle(self):
        """Estilo CSS para el contenedor del footer"""
        return """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 rgba(240, 255, 240, 0.8), 
                            stop:1 rgba(224, 255, 224, 0.8));
                border-top: 2px solid rgba(50, 205, 50, 0.3);
                border-radius: 0px 0px 15px 15px;
            }
        """
        
    def getDeveloperStyle(self):
        """Estilo CSS para información del desarrollador"""
        return """
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #228B22;
                padding: 8px;
                letter-spacing: 0.5px;
            }
        """
        
    def getInstitutionStyle(self):
        """Estilo CSS para información institucional"""
        return """
            QLabel {
                font-size: 14px;
                color: #2F4F2F;
                font-style: italic;
                letter-spacing: 0.5px;
            }
        """

class CompactFooter(QFrame):
    """Version compacta del footer para espacios reducidos"""
    
    def __init__(self):
        super().__init__()
        self.setFixedHeight(60)
        self.setStyleSheet(self.getCompactStyle())
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        footer_text = QLabel("AGRIOT - José Vicente Rincón • UNAB 2025")
        footer_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_text.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 500;
                color: #228B22;
            }
        """)
        
        layout.addWidget(footer_text)
        
    def getCompactStyle(self):
        """Estilo para footer compacto"""
        return """
            QFrame {
                background: rgba(240, 255, 240, 0.6);
                border-top: 1px solid rgba(50, 205, 50, 0.2);
            }
        """

class AnimatedFooter(ModernFooter):
    """Footer con efectos de animación sutiles"""
    
    def __init__(self, height=100):
        super().__init__(height)
        
    def getFooterStyle(self):
        """Estilo animado para el footer"""
        return """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 rgba(240, 255, 240, 0.9), 
                            stop:0.5 rgba(224, 255, 224, 0.8),
                            stop:1 rgba(240, 255, 240, 0.9));
                border-top: 2px solid rgba(50, 205, 50, 0.4);
                border-radius: 0px 0px 20px 20px;
            }
        """
        
    def getDeveloperStyle(self):
        """Estilo animado para desarrollador"""
        return """
            QLabel {
                font-size: 16px;
                font-weight: 700;
                color: #228B22;
                padding: 8px;
                letter-spacing: 1px;
            }
        """