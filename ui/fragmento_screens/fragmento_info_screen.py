from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

class FragmentoInfoScreen(QWidget):
    """Pantalla para mostrar información de los videos originales"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.title = QLabel("Información de Videos Originales")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px;")
        self.layout().addWidget(self.title)

        self.btn_back = QPushButton("Volver")
        self.layout().addWidget(self.btn_back)
        self.btn_back.clicked.connect(self.volver)

    def volver(self):
        if self.parent():
            self.parent().setCurrentIndex(0)
