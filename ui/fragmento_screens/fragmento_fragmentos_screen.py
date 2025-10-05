from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QTextEdit
from PySide6.QtCore import Qt
from pathlib import Path

class FragmentoFragmentosScreen(QWidget):
    """Pantalla para explorar fragmentos generados"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.cargar_fragmentos()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        title = QLabel("Fragmentos Generados por Entrevista")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        self.fragment_list = QListWidget()
        layout.addWidget(self.fragment_list)

        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.details.setPlaceholderText("Detalles del fragmento seleccionado...")
        layout.addWidget(self.details)

        self.btn_volver = QPushButton("Volver al Menú de Fragmentos")
        self.btn_volver.clicked.connect(self.volver)
        layout.addWidget(self.btn_volver)

        self.fragment_list.itemClicked.connect(self.mostrar_detalle)

    def cargar_fragmentos(self):
        """Carga los fragmentos disponibles"""
        folder = Path("data/fragmentos")
        self.fragment_list.clear()
        if not folder.exists():
            self.fragment_list.addItem("⚠️ Carpeta no encontrada")
            return
        for frag in folder.glob("*.mp4"):
            self.fragment_list.addItem(frag.name)

    def mostrar_detalle(self, item):
        """Muestra información del fragmento seleccionado"""
        fragmento_path = Path("data/fragmentos") / item.text()
        if fragmento_path.exists():
            size = round(fragmento_path.stat().st_size / (1024 * 1024), 2)
            self.details.setPlainText(
                f"📄 Nombre: {fragmento_path.name}\n"
                f"📏 Tamaño: {size} MB\n"
                f"📂 Ruta: {fragmento_path}\n"
                f"🕓 (Duración y comentario se integrarán luego con metadatos)"
            )

    def volver(self):
        """Regresar al menú principal del módulo"""
        if self.parent():
            self.parent().setCurrentIndex(0)
