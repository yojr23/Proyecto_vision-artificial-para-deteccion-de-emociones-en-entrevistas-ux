import logging
import os
import json
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QHeaderView, QPushButton, QFrame, 
    QTextEdit, QSplitter, QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter
import cv2
import subprocess

# Importar las clases de marcas
from classes.marca import Marca
from classes.marcas import Marcas


class AnalisisInfoScreen(QWidget):
    def __init__(self, logger = None, data_context= None,parent=None):
        super().__init__(parent)
        self.logger = logger or logging.getLogger(__name__)
        self.parent_window = parent
        self.videos_data = []
        self.data_context = data_context or {"videos": [], "marcas": {}, "fragmentos": []}
        self.setup_ui()