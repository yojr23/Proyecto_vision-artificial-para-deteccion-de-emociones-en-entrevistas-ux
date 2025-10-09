import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QMessageBox, QStackedWidget, QFrame, QScrollArea, QPushButton
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPixmap, QPainter

# Importar componentes
from .utils.buttons import ModernButton
from .utils.footer import AnimatedFooter
from .utils.styles import (
    ColorPalette, GradientStyles, CommonStyles, 
    MessageBoxStyles, LayoutSettings, FontSettings
)

# 🔹 Definir paleta de colores verde agrícola completa
AGRICULTURAL_GREEN_PALETTE = {
    'DARK_GREEN': '#1b5e20',
    'PRIMARY_GREEN': '#2e7d32', 
    'MEDIUM_GREEN': '#388e3c',
    'LIGHT_GREEN': '#4caf50',
    'SOFT_GREEN': '#66bb6a',
    'BRIGHT_GREEN': '#81c784',
    'PALE_GREEN': '#a5d6a7',
    'MINT_GREEN': '#c8e6c9',
    'WHITE_GREEN': '#e8f5e9',
    'FOREST_GREEN': '#2e572c',
    'SPRING_GREEN': '#43a047',
    'GRASS_GREEN': '#558b2f',
    'LEAF_GREEN': '#689f38'
}


class ConfigMainWindow(QMainWindow):
    def __init__(self, parent=None, logger=None):
        super().__init__(parent)
        self.logger = logger or logging.getLogger(__name__)
        self.setWindowTitle("Módulo de Configuración - AGRIOT")
        self.resize(1400, 800)
