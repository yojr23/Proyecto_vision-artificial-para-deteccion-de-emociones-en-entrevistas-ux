import logging
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QPushButton, QLineEdit, QTextEdit, QMessageBox, QFrame,
    QListWidgetItem, QDialog, QDialogButtonBox, QComboBox, QFileDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon

from ..utils.buttons import ModernButton
from ..utils.styles import ColorPalette

# Import the EntrevistaPreguntas class
from classes.entrevista_preguntas import EntrevistaPreguntas


class ConfigPreguntaScreen(QWidget):
    """Pantalla para configurar las preguntas de la entrevista"""
    
    preguntas_actualizadas = Signal()  # Señal para notificar cambios
    
    def __init__(self, parent=None, logger=None):
        super().__init__(parent)
        self.logger = logger or logging.getLogger(__name__)
        self.preguntas_file = Path("data/preguntas.json")
        self.entrevista = EntrevistaPreguntas()
        self.cambios_pendientes = False
        
        self.setup_ui()
        self.cargar_preguntas()
        
    def setup_ui(self):
        """Construir la interfaz de configuración de preguntas"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # 🔸 Título de la sección
        title_label = QLabel("📝 Gestión de Preguntas de Entrevista")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {ColorPalette.DARK_GREEN};
                padding: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(232, 245, 233, 0.8),
                    stop:1 rgba(200, 230, 201, 0.8));
                border-radius: 15px;
                border: 2px solid {ColorPalette.LIGHT_GREEN};
            }}
        """)
        main_layout.addWidget(title_label)
        
        # 🔸 Descripción
        desc_label = QLabel(
            "Configura las preguntas que se realizarán durante las entrevistas. "
            "Puedes agregar, editar, eliminar y reordenar las preguntas por categoría."
        )
        desc_label.setWordWrap(True)
        desc_label.setFont(QFont("Segoe UI", 11))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: #2d5016;
                padding: 10px 20px;
                background: rgba(255, 255, 255, 0.7);
                border-radius: 10px;
                border: 1px solid {ColorPalette.SOFT_GREEN};
            }}
        """)
        main_layout.addWidget(desc_label)
        
        # 🔸 Contenedor principal con dos columnas
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # --- Columna izquierda: Lista de preguntas ---
        left_frame = self.create_lista_preguntas_frame()
        content_layout.addWidget(left_frame, stretch=2)
        
        # --- Columna derecha: Botones de acción ---
        right_frame = self.create_acciones_frame()
        content_layout.addWidget(right_frame, stretch=1)
        
        main_layout.addLayout(content_layout, stretch=1)
        
        # 🔸 Panel de estadísticas
        stats_frame = self.create_estadisticas_frame()
        main_layout.addWidget(stats_frame)
        
    def create_lista_preguntas_frame(self):
        """Crear frame con la lista de preguntas"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                border: 2px solid {ColorPalette.LIGHT_GREEN};
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        
        # Título
        title = QLabel("📋 Lista de Preguntas")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ColorPalette.DARK_GREEN};")
        layout.addWidget(title)
        
        # Selector de categoría
        cat_label = QLabel("Categoría:")
        cat_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        cat_label.setStyleSheet(f"color: {ColorPalette.DARK_GREEN};")
        layout.addWidget(cat_label)
        
        self.combo_categoria = QComboBox()
        self.combo_categoria.setStyleSheet(f"""
            QComboBox {{
                background: white;
                border: 2px solid {ColorPalette.SOFT_GREEN};
                border-radius: 8px;
                padding: 8px;
                font-size: 11px;
                min-height: 35px;
                color: black;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {ColorPalette.DARK_GREEN};
            }}
        """)
        self.combo_categoria.currentTextChanged.connect(self.cambiar_categoria)
        layout.addWidget(self.combo_categoria)
        
        # Lista de preguntas
        self.lista_preguntas = QListWidget()
        self.lista_preguntas.setFont(QFont("Segoe UI", 11))
        self.lista_preguntas.setStyleSheet(f"""
            QListWidget {{
                background: white;
                border: 2px solid {ColorPalette.SOFT_GREEN};
                border-radius: 10px;
                padding: 5px;
                color: #1a237e;
            }}
            QListWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {ColorPalette.PALE_GREEN};
                border-radius: 5px;
                margin: 2px;
            }}
            QListWidget::item:selected {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ColorPalette.LIGHT_GREEN},
                    stop:1 {ColorPalette.SOFT_GREEN});
                color: black;
                font-weight: 600;
            }}
            QListWidget::item:hover {{
                background: rgba(76, 175, 80, 0.2);
            }}
        """)
        self.lista_preguntas.itemDoubleClicked.connect(self.editar_pregunta)
        layout.addWidget(self.lista_preguntas)
        
        return frame
        
    def create_acciones_frame(self):
        """Crear frame con botones de acción"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                border: 2px solid {ColorPalette.LIGHT_GREEN};
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignTop)
        
        # Título
        title = QLabel("⚡ Acciones")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ColorPalette.DARK_GREEN};")
        layout.addWidget(title)
        
        # Botones de acción
        btn_agregar = ModernButton("➕ Agregar Pregunta", button_type="primary")
        btn_editar = ModernButton("✏️ Editar Pregunta", button_type="secondary")
        btn_eliminar = ModernButton("🗑️ Eliminar Pregunta", button_type="accent")
        btn_subir = ModernButton("⬆️ Subir", button_type="secondary")
        btn_bajar = ModernButton("⬇️ Bajar", button_type="secondary")
        btn_guardar = ModernButton("💾 Guardar Cambios", button_type="primary")
        btn_resetear = ModernButton("🔄 Resetear Default", button_type="accent")
        btn_descargar = ModernButton("⬇️ Descargar Preguntas", button_type="primary")
        
        # Aplicar estilos
        button_style = """
            QPushButton {
                min-height: 45px;
                font-size: 13px;
                font-weight: 600;
                color: black;
            }
        """
        
        for btn in [btn_agregar, btn_editar, btn_eliminar, btn_subir, 
                    btn_bajar, btn_guardar, btn_resetear, btn_descargar]:
            btn.setStyleSheet(btn.styleSheet() + button_style)
        
        # Conectar señales
        btn_agregar.clicked.connect(self.agregar_pregunta)
        btn_editar.clicked.connect(self.editar_pregunta)
        btn_eliminar.clicked.connect(self.eliminar_pregunta)
        btn_subir.clicked.connect(self.subir_pregunta)
        btn_bajar.clicked.connect(self.bajar_pregunta)
        btn_guardar.clicked.connect(self.guardar_preguntas)
        btn_resetear.clicked.connect(self.resetear_preguntas_default)
        btn_descargar.clicked.connect(self.descargar_preguntas)
        
        # Agregar botones
        layout.addWidget(btn_agregar)
        layout.addWidget(btn_editar)
        layout.addWidget(btn_eliminar)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background: {ColorPalette.SOFT_GREEN}; max-height: 2px;")
        layout.addWidget(separator)
        
        layout.addWidget(btn_subir)
        layout.addWidget(btn_bajar)
        
        # Separador
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setStyleSheet(f"background: {ColorPalette.SOFT_GREEN}; max-height: 2px;")
        layout.addWidget(separator2)
        
        layout.addWidget(btn_guardar)
        layout.addWidget(btn_resetear)
        layout.addWidget(btn_descargar)
        
        # Espaciador
        layout.addStretch()
        
        return frame
        
    def create_estadisticas_frame(self):
        """Crear panel de estadísticas"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(232, 245, 233, 0.9),
                    stop:1 rgba(200, 230, 201, 0.9));
                border-radius: 12px;
                border: 2px solid {ColorPalette.LIGHT_GREEN};
                padding: 12px;
            }}
        """)
        
        layout = QHBoxLayout(frame)
        layout.setSpacing(20)
        
        # Total de preguntas
        self.label_total = QLabel("📊 Total de preguntas: 0")
        self.label_total.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.label_total.setStyleSheet(f"color: {ColorPalette.DARK_GREEN};")
        
        # Estado de guardado
        self.label_estado = QLabel("✅ Cambios guardados")
        self.label_estado.setFont(QFont("Segoe UI", 11))
        self.label_estado.setStyleSheet(f"color: {ColorPalette.PRIMARY_GREEN};")
        
        layout.addWidget(self.label_total)
        layout.addStretch()
        layout.addWidget(self.label_estado)
        
        return frame
        
    # ------------------------------------------------------------------
    # 🔹 Gestión de preguntas
    # ------------------------------------------------------------------
    
    def cargar_preguntas(self):
        """Cargar preguntas desde el archivo JSON"""
        try:
            if self.preguntas_file.exists():
                success = self.entrevista.importar_json(str(self.preguntas_file))
                if not success:
                    self.logger.warning("No se pudo importar, usando valores por defecto")
                    # Forzar reset a defaults si falla la importación
                    self.entrevista = EntrevistaPreguntas()
                    self.entrevista.exportar_json(str(self.preguntas_file))
            else:
                self.entrevista.exportar_json(str(self.preguntas_file))
            
            self.actualizar_combo_categorias()
            self.cambiar_categoria()  # Actualiza la lista con la primera categoría
            self.cambios_pendientes = False
            self.label_estado.setText("✅ Cambios guardados")
            self.label_estado.setStyleSheet(f"color: {ColorPalette.PRIMARY_GREEN};")
            self.logger.info(f"Preguntas cargadas: {self.entrevista.total_preguntas}")
            
        except Exception as e:
            self.logger.error(f"Error cargando preguntas: {str(e)}")
            self.show_error(f"Error al cargar preguntas: {str(e)}")
            
    def guardar_preguntas(self):
        """Guardar preguntas en el archivo JSON"""
        try:
            # Asegurar que el directorio existe
            self.preguntas_file.parent.mkdir(parents=True, exist_ok=True)
            
            self.entrevista.exportar_json(str(self.preguntas_file))
            
            self.cambios_pendientes = False
            self.label_estado.setText("✅ Cambios guardados")
            self.label_estado.setStyleSheet(f"color: {ColorPalette.PRIMARY_GREEN};")
            self.logger.info(f"Preguntas guardadas: {self.entrevista.total_preguntas}")
            self.preguntas_actualizadas.emit()
            
            self.show_info("Preguntas guardadas exitosamente.")
            
        except Exception as e:
            self.logger.error(f"Error guardando preguntas: {str(e)}")
            self.show_error(f"Error al guardar preguntas: {str(e)}")
            
    def actualizar_combo_categorias(self):
        """Actualizar el combo de categorías"""
        current_cat = self.combo_categoria.currentText()
        self.combo_categoria.clear()
        categorias = sorted(self.entrevista.preguntas.keys())
        self.combo_categoria.addItems(categorias)
        
        # Seleccionar la primera categoría automáticamente si no hay una preseleccionada
        if self.combo_categoria.count() > 0 and not current_cat:
            self.combo_categoria.setCurrentIndex(0)
        elif current_cat in categorias:
            self.combo_categoria.setCurrentText(current_cat)
            
    def cambiar_categoria(self):
        """Cambiar la categoría seleccionada y actualizar lista"""
        self.actualizar_lista()
        
    def actualizar_lista(self):
        """Actualizar la lista visual de preguntas"""
        self.lista_preguntas.clear()
        
        current_cat = self.combo_categoria.currentText()
        if not current_cat:
            return
            
        cat_preguntas = self.entrevista.preguntas.get(current_cat, [])
        
        for i, pregunta in enumerate(cat_preguntas, 1):
            texto = pregunta.get("texto", "Sin texto")
            item_text = f"{i}. {texto}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, i - 1)  # Guardar índice dentro de la categoría
            self.lista_preguntas.addItem(item)
        
        # Actualizar estadísticas
        self.label_total.setText(f"📊 Total de preguntas: {self.entrevista.total_preguntas}")
        
        if self.cambios_pendientes:
            self.marcar_cambios_pendientes()
        
    def marcar_cambios_pendientes(self):
        """Marcar que hay cambios sin guardar"""
        self.label_estado.setText("⚠️ Cambios sin guardar")
        self.label_estado.setStyleSheet("color: #f57c00;")
        
    def get_categoria_actual(self):
        """Obtener la categoría actual seleccionada"""
        return self.combo_categoria.currentText()
    
    def agregar_pregunta(self):
        """Agregar una nueva pregunta"""
        categoria = self.get_categoria_actual()
        if not categoria:
            self.show_warning("Por favor, selecciona una categoría.")
            return
            
        dialog = PreguntaDialog(parent=self, titulo="Agregar Pregunta")
        
        if dialog.exec() == QDialog.Accepted:
            nueva_pregunta = dialog.get_pregunta()
            if self.entrevista.crear_pregunta(categoria, nueva_pregunta):
                self.cambios_pendientes = True
                self.actualizar_lista()
                self.logger.info(f"Pregunta agregada en {categoria}: {nueva_pregunta['texto']}")
            else:
                self.show_error("Error al agregar la pregunta.")
                
    def editar_pregunta(self):
        """Editar la pregunta seleccionada"""
        current_item = self.lista_preguntas.currentItem()
        
        if not current_item:
            self.show_warning("Por favor, selecciona una pregunta para editar.")
            return
        
        categoria = self.get_categoria_actual()
        if not categoria:
            self.show_warning("Por favor, selecciona una categoría.")
            return
            
        index = current_item.data(Qt.UserRole)
        pregunta_actual = self.entrevista.obtener_pregunta(categoria, index)
        
        if not pregunta_actual:
            self.show_error("Error al obtener la pregunta.")
            return
        
        dialog = PreguntaDialog(
            parent=self, 
            titulo="Editar Pregunta",
            pregunta_data=pregunta_actual
        )
        
        if dialog.exec() == QDialog.Accepted:
            pregunta_editada = dialog.get_pregunta()
            if self.entrevista.actualizar_pregunta(categoria, index, pregunta_editada):
                self.cambios_pendientes = True
                self.actualizar_lista()
                self.logger.info(f"Pregunta editada en {categoria}: {pregunta_editada['texto']}")
            else:
                self.show_error("Error al editar la pregunta.")
                
    def eliminar_pregunta(self):
        """Eliminar la pregunta seleccionada"""
        current_item = self.lista_preguntas.currentItem()
        
        if not current_item:
            self.show_warning("Por favor, selecciona una pregunta para eliminar.")
            return
        
        categoria = self.get_categoria_actual()
        if not categoria:
            self.show_warning("Por favor, selecciona una categoría.")
            return
            
        index = current_item.data(Qt.UserRole)
        pregunta = self.entrevista.obtener_pregunta(categoria, index)
        
        if not pregunta:
            self.show_error("Error al obtener la pregunta.")
            return
        
        respuesta = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Estás seguro de eliminar la pregunta:\n\n'{pregunta['texto']}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            if self.entrevista.eliminar_pregunta(categoria, index):
                self.cambios_pendientes = True
                self.actualizar_lista()
                self.logger.info(f"Pregunta eliminada en {categoria}: {pregunta['texto']}")
            else:
                self.show_error("Error al eliminar la pregunta.")
                
    def subir_pregunta(self):
        """Subir la pregunta seleccionada en la lista"""
        current_item = self.lista_preguntas.currentItem()
        
        if not current_item:
            self.show_warning("Por favor, selecciona una pregunta.")
            return
        
        categoria = self.get_categoria_actual()
        if not categoria:
            self.show_warning("Por favor, selecciona una categoría.")
            return
            
        index = current_item.data(Qt.UserRole)
        
        if self.entrevista.subir_pregunta(categoria, index):
            self.cambios_pendientes = True
            self.actualizar_lista()
            self.lista_preguntas.setCurrentRow(index - 1)
        else:
            self.show_info("La pregunta ya está en la primera posición.")
        
    def bajar_pregunta(self):
        """Bajar la pregunta seleccionada en la lista"""
        current_item = self.lista_preguntas.currentItem()
        
        if not current_item:
            self.show_warning("Por favor, selecciona una pregunta.")
            return
        
        categoria = self.get_categoria_actual()
        if not categoria:
            self.show_warning("Por favor, selecciona una categoría.")
            return
            
        index = current_item.data(Qt.UserRole)
        
        if self.entrevista.bajar_pregunta(categoria, index):
            self.cambios_pendientes = True
            self.actualizar_lista()
            self.lista_preguntas.setCurrentRow(index + 1)
        else:
            self.show_info("La pregunta ya está en la última posición.")
        
    def resetear_preguntas_default(self):
        """Resetear a las preguntas por defecto"""
        respuesta = QMessageBox.question(
            self,
            "Confirmar Reseteo",
            "¿Estás seguro de resetear las preguntas a los valores por defecto?\n\n"
            "Se perderán todas las preguntas personalizadas.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            self.entrevista = EntrevistaPreguntas()
            self.cargar_preguntas()  # Recarga y actualiza UI
            self.guardar_preguntas()
            self.logger.info("Preguntas reseteadas a valores por defecto")
    
    def descargar_preguntas(self):
        """Permite descargar las preguntas en JSON o PDF"""
        opciones = ["JSON (*.json)", "PDF (*.pdf)"]
        archivo, filtro = QFileDialog.getSaveFileName(
            self,
            "Guardar preguntas como",
            "",
            ";;".join(opciones)
        )
        if not archivo:
            return
        
        try:
            if filtro.startswith("JSON"):
                # Exportar como JSON
                self.entrevista.exportar_json(archivo)
                self.show_info(f"Preguntas guardadas correctamente en JSON:\n{archivo}")
            else:
                # Exportar como PDF (requiere fpdf2 instalado)
                try:
                    from fpdf import FPDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    pdf.set_font("Arial", 'B', 14)
                    pdf.cell(0, 10, "Preguntas de Entrevista", ln=True, align="C")
                    pdf.ln(5)
                    pdf.set_font("Arial", '', 12)
                    
                    for categoria, preguntas in self.entrevista.preguntas.items():
                        pdf.set_font("Arial", 'B', 12)
                        pdf.cell(0, 8, categoria, ln=True)
                        pdf.set_font("Arial", '', 12)
                        for i, p in enumerate(preguntas, 1):
                            texto = p.get("texto", "")
                            pdf.multi_cell(0, 7, f"{i}. {texto}")
                        pdf.ln(3)
                    
                    if not archivo.lower().endswith(".pdf"):
                        archivo += ".pdf"
                    pdf.output(archivo)
                    self.show_info(f"Preguntas guardadas correctamente en PDF:\n{archivo}")
                except ImportError:
                    self.show_error("Para exportar a PDF, instala fpdf2: pip install fpdf2")
                    
        except Exception as e:
            self.logger.error(f"Error descargando preguntas: {str(e)}")
            self.show_error(f"Error al descargar preguntas:\n{str(e)}")
    
    # ------------------------------------------------------------------
    # 🔹 Utilidades
    # ------------------------------------------------------------------
    
    def show_error(self, msg):
        QMessageBox.critical(self, "Error", msg)
        
    def show_warning(self, msg):
        QMessageBox.warning(self, "Advertencia", msg)
        
    def show_info(self, msg):
        QMessageBox.information(self, "Información", msg)


# ------------------------------------------------------------------
# 🔹 Diálogo para agregar/editar preguntas
# ------------------------------------------------------------------

class PreguntaDialog(QDialog):
    """Diálogo para agregar o editar una pregunta"""
    
    def __init__(self, parent=None, titulo="Pregunta", pregunta_data=None):
        super().__init__(parent)
        self.pregunta_data = pregunta_data or {}
        self.setWindowTitle(titulo)
        self.setModal(True)
        self.resize(600, 400)
        
        # Inicializar widgets antes de usarlos
        self.input_texto = QTextEdit()
        self.input_tipo = QLineEdit()
        self.check_requerida = QPushButton("✓ Sí, es requerida")
        
        self.setup_ui()
        self.cargar_datos()
        
    def setup_ui(self):
        """Construir la interfaz del diálogo"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Estilo general del diálogo
        self.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.98),
                    stop:1 rgba(232, 245, 233, 0.98));
            }}
            QLabel {{
                color: {ColorPalette.DARK_GREEN};
                font-weight: 600;
                font-size: 12px;
            }}
            QLineEdit, QTextEdit {{
                border: 2px solid {ColorPalette.SOFT_GREEN};
                border-radius: 8px;
                padding: 8px;
                background: white;
                font-size: 11px;
                color: black;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 2px solid {ColorPalette.LIGHT_GREEN};
                color: black;
            }}
        """)
        
        # Campo: Texto de la pregunta
        label_texto = QLabel("Texto de la pregunta:")
        self.input_texto.setPlaceholderText("Escribe aquí la pregunta...")
        self.input_texto.setMaximumHeight(100)
        layout.addWidget(label_texto)
        layout.addWidget(self.input_texto)
        
        # Campo: Tipo de pregunta
        label_tipo = QLabel("Tipo de respuesta:")
        self.input_tipo.setText("text")
        self.input_tipo.setPlaceholderText("text, numeric, etc.")
        layout.addWidget(label_tipo)
        layout.addWidget(self.input_tipo)
        
        # Campo: Requerida
        label_requerida = QLabel("¿Es requerida?")
        self.check_requerida.setCheckable(True)
        self.check_requerida.setChecked(True)
        self.check_requerida.setStyleSheet(f"""
            QPushButton {{
                background: {ColorPalette.LIGHT_GREEN};
                color: black;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: 600;
            }}
            QPushButton:checked {{
                background: {ColorPalette.PRIMARY_GREEN};
                color: black;
            }}
            QPushButton:hover {{
                background: {ColorPalette.SOFT_GREEN};
                color: black;
            }}
        """)
        layout.addWidget(label_requerida)
        layout.addWidget(self.check_requerida)
        
        # Espaciador
        layout.addStretch()
        
        # Botones de acción
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.validar_y_aceptar)
        button_box.rejected.connect(self.reject)
        button_box.setStyleSheet(f"""
            QPushButton {{
                background: {ColorPalette.LIGHT_GREEN};
                color: black;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: {ColorPalette.PRIMARY_GREEN};
            }}
        """)
        layout.addWidget(button_box)
        
    def cargar_datos(self):
        """Cargar datos si se está editando una pregunta"""
        if self.pregunta_data:
            self.input_texto.setPlainText(self.pregunta_data.get("texto", ""))
            self.input_tipo.setText(self.pregunta_data.get("tipo", "text"))
            self.check_requerida.setChecked(self.pregunta_data.get("requerida", True))
            
    def validar_y_aceptar(self):
        """Validar datos antes de aceptar"""
        texto = self.input_texto.toPlainText().strip()
        
        if not texto:
            QMessageBox.warning(self, "Validación", "El texto de la pregunta no puede estar vacío.")
            return
        
        self.accept()
        
    def get_pregunta(self):
        """Obtener los datos de la pregunta"""
        return {
            "texto": self.input_texto.toPlainText().strip(),
            "tipo": self.input_tipo.text().strip() or "text",
            "requerida": self.check_requerida.isChecked()
        }