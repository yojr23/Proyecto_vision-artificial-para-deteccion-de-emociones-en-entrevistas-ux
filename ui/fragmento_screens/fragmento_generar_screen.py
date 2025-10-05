from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QProgressBar, QTextEdit
)
from PySide6.QtCore import Qt, QThread, Signal
from pathlib import Path

class FragmentoGenerarScreen(QWidget):
    """Pantalla para seleccionar video y generar fragmentos"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.video_seleccionado = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        title = QLabel("Generar Fragmentos")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        self.btn_select = QPushButton("Seleccionar Video Original")
        self.btn_select.clicked.connect(self.seleccionar_video)
        layout.addWidget(self.btn_select)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Aquí aparecerá el registro del proceso...")
        layout.addWidget(self.log_output)

        self.btn_generar = QPushButton("Generar Fragmentos")
        self.btn_generar.clicked.connect(self.generar_fragmentos)
        layout.addWidget(self.btn_generar)

        self.btn_volver = QPushButton("Volver al Menú de Fragmentos")
        self.btn_volver.clicked.connect(self.volver)
        layout.addWidget(self.btn_volver)

    def seleccionar_video(self):
        """Selecciona un video desde el sistema"""
        file, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar video original", "data/videos_originales", "Videos (*.mp4 *.mov)"
        )
        if file:
            self.video_seleccionado = Path(file)
            self.log_output.append(f"🎞 Video seleccionado: {self.video_seleccionado.name}")

    def generar_fragmentos(self):
        """Simula el proceso de generación de fragmentos"""
        if not self.video_seleccionado:
            self.log_output.append("⚠️ No se ha seleccionado ningún video.")
            return
        self.log_output.append("⏳ Iniciando generación de fragmentos (simulación)...")
        self.progress.setValue(50)
        # Aquí luego se integrará el llamado real a la clase Fragmento
        self.progress.setValue(100)
        self.log_output.append("✅ Fragmentos generados correctamente.")

    def volver(self):
        """Regresar al menú principal del módulo"""
        if self.parent():
            self.parent().setCurrentIndex(0)
