import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QMessageBox, QStackedWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Importar componentes
from .utils.buttons import ModernButton
from .utils.footer import AnimatedFooter
from .fragmento_screens.fragmento_info_screen import FragmentoInfoScreen
from .fragmento_screens.fragmento_generar_screen import FragmentoGenerarScreen
from .fragmento_screens.fragmento_fragmentos_screen import FragmentoFragmentosScreen


class FragmentoMainWindow(QMainWindow):
    def __init__(self, parent=None, logger=None):
        super().__init__(parent)
        self.logger = logger or logging.getLogger(__name__)
        self.setWindowTitle("Módulo de Fragmentos - AGRIOT")
        self.resize(1400, 800)

        self._check_directories()
        self.setup_ui()

    # ------------------------------------------------------------------
    # 🔹 Verificar carpetas
    # ------------------------------------------------------------------
    def _check_directories(self):
        self.Originales_path = Path("data/videos_originales")
        self.Marcas_path = Path("data/marcas")
        self.Fragmentos_path = Path("data/fragmentos")

        for path in [self.Originales_path, self.Marcas_path, self.Fragmentos_path]:
            if not path.is_dir():
                raise ValueError(f"El directorio {path} no existe o no es válido")

    # ------------------------------------------------------------------
    # 🔹 Construcción de la interfaz
    # ------------------------------------------------------------------
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)

        # 🔸 Título
        title = QLabel("Gestor de Fragmentos de Entrevistas")
        title.setFont(QFont("Arial", 24))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1a1a1a; padding: 20px;")
        main_layout.addWidget(title)

        # 🔸 Stack de pantallas
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, stretch=1)

        # Agregar subpantallas
        self.info_screen = FragmentoInfoScreen(self)
        self.generar_screen = FragmentoGenerarScreen(self)
        self.fragmentos_screen = FragmentoFragmentosScreen(self)

        self.stack.addWidget(self.info_screen)
        self.stack.addWidget(self.generar_screen)
        self.stack.addWidget(self.fragmentos_screen)

        # 🔸 Menú inferior
        menu_layout = QHBoxLayout()
        menu_layout.setAlignment(Qt.AlignCenter)
        menu_layout.setSpacing(15)

        btn_info = ModernButton("Información de Videos")
        btn_generar = ModernButton("Generar Fragmentos")
        btn_ver = ModernButton("Ver Fragmentos")
        btn_volver = ModernButton("Volver al Menú Principal")

        btn_info.clicked.connect(lambda: self.stack.setCurrentWidget(self.info_screen))
        btn_generar.clicked.connect(lambda: self.stack.setCurrentWidget(self.generar_screen))
        btn_ver.clicked.connect(lambda: self.stack.setCurrentWidget(self.fragmentos_screen))
        btn_volver.clicked.connect(self.volver_menu_principal)

        for btn in [btn_info, btn_generar, btn_ver, btn_volver]:
            menu_layout.addWidget(btn)

        main_layout.addLayout(menu_layout)

        # 🔸 Footer
        footer = AnimatedFooter()
        main_layout.addWidget(footer)

    # ------------------------------------------------------------------
    # 🔹 Volver al menú principal
    # ------------------------------------------------------------------
    def volver_menu_principal(self):
        """Cerrar la ventana y mostrar el menú principal"""
        self.logger.info("Cerrando módulo de fragmentos y volviendo al menú principal...")
        if self.parent():
            self.parent().show()
        self.close()
