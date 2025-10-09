import os
import json
import logging
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QFrame,
    QTextEdit, QSplitter, QMessageBox, QProgressBar,
    QComboBox, QListWidget, QListWidgetItem, QGroupBox,
    QFileDialog, QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap, QPainter

class AnalisisReporteScreen(QWidget):
    def __init__(self, logger=None, data_context=None, parent=None):
        super().__init__(parent)
        self.logger = logger or logging.getLogger(__name__)
        self.parent_window = parent
        self.videos_data = []
        self.data_context = data_context or {"videos": [], "marcas": {}, "fragmentos": []}
        self.setup_ui()