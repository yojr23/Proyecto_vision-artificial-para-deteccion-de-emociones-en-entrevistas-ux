import logging
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QComboBox, QCheckBox, QProgressBar, QFileDialog, QMessageBox,
    QGroupBox, QButtonGroup, QRadioButton
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
import matplotlib.pyplot as plt
import numpy as np

from ..utils.styles import ColorPalette

class ExportWorker(QThread):
    progress = Signal(int)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, data_context, entrevista_id, options):
        super().__init__()
        self.data_context = data_context
        self.entrevista_id = entrevista_id
        self.options = options

    def run(self):
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
                zip_path = tmp_file.name

            with zipfile.ZipFile(zip_path, 'w') as zipf:
                # Exportar gráficos según opciones
                if self.options.get('global_chart', True):
                    self.export_global_chart(zipf)
                
                if self.options.get('individual_charts', True):
                    self.export_individual_charts(zipf)
                
                if self.options.get('data_json', True):
                    self.export_json_data(zipf)

            self.finished.emit(zip_path)
            
        except Exception as e:
            self.error.emit(str(e))

    def export_global_chart(self, zipf):
        """Exportar gráfico global"""
        # Implementar generación de gráfico global
        self.progress.emit(25)

    def export_individual_charts(self, zipf):
        """Exportar gráficos individuales"""
        # Implementar generación de gráficos individuales
        self.progress.emit(75)

    def export_json_data(self, zipf):
        """Exportar datos en JSON"""
        # Implementar exportación de datos
        self.progress.emit(100)

class ExportScreen(QWidget):
    def __init__(self, logger=None, data_context=None, parent=None):
        super().__init__(parent)
        self.logger = logger or logging.getLogger(__name__)
        self.data_context = data_context or {}
        self.current_entrevista_id = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Título
        title = QLabel("📤 Exportar Reportes")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #1b5e20;
                background: rgba(255, 255, 255, 0.9);
                padding: 20px;
                border-radius: 20px;
                border: 3px solid #4caf50;
                margin: 10px;
            }
        """)
        layout.addWidget(title)

        # Panel de configuración
        config_frame = self.crear_panel_configuracion()
        layout.addWidget(config_frame)

        # Panel de progreso
        self.progress_frame = self.crear_panel_progreso()
        layout.addWidget(self.progress_frame)

        # Botones de acción
        button_frame = self.crear_panel_botones()
        layout.addWidget(button_frame)

    def crear_panel_configuracion(self):
        """Crear panel de configuración de exportación"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                border: 2px solid #c8e6c9;
                padding: 25px;
            }
        """)
        layout = QVBoxLayout(frame)

        # Grupo de formato
        format_group = QGroupBox("📁 Formato de Exportación")
        format_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        format_group.setStyleSheet("""
            QGroupBox {
                color: #2e7d32;
                background: rgba(248, 255, 248, 0.9);
                border: 2px solid #a5d6a7;
                border-radius: 15px;
                margin-top: 12px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
            }
        """)
        
        format_layout = QHBoxLayout(format_group)
        self.format_zip = QRadioButton("ZIP (Gráficos + Datos)")
        self.format_pdf = QRadioButton("PDF (Reporte completo)")
        self.format_zip.setChecked(True)
        
        for rb in [self.format_zip, self.format_pdf]:
            rb.setFont(QFont("Segoe UI", 10))
            rb.setStyleSheet("color: #555; padding: 8px;")
            format_layout.addWidget(rb)
        
        format_layout.addStretch()
        layout.addWidget(format_group)

        # Grupo de contenido
        content_group = QGroupBox("📊 Contenido a Exportar")
        content_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        content_group.setStyleSheet(format_group.styleSheet())
        
        content_layout = QVBoxLayout(content_group)
        
        self.chk_global = QCheckBox("Gráfico araña global")
        self.chk_individual = QCheckBox("Gráficos por pregunta")
        self.chk_data = QCheckBox("Datos en JSON")
        self.chk_stats = QCheckBox("Estadísticas resumen")
        
        for chk in [self.chk_global, self.chk_individual, self.chk_data, self.chk_stats]:
            chk.setChecked(True)
            chk.setFont(QFont("Segoe UI", 10))
            chk.setStyleSheet("color: #555; padding: 6px;")
            content_layout.addWidget(chk)
        
        layout.addWidget(content_group)

        return frame

    def crear_panel_progreso(self):
        """Crear panel de progreso (inicialmente oculto)"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                border: 2px solid #c8e6c9;
                padding: 25px;
            }
        """)
        layout = QVBoxLayout(frame)
        
        self.progress_label = QLabel("Preparando exportación...")
        self.progress_label.setFont(QFont("Segoe UI", 11))
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("color: #555; padding: 10px;")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #c8e6c9;
                border-radius: 10px;
                text-align: center;
                background: #f1f8e9;
                height: 25px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4caf50, stop:1 #2e7d32);
                border-radius: 8px;
            }
        """)
        
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        frame.hide()  # Oculto inicialmente
        
        return frame

    def crear_panel_botones(self):
        """Crear panel de botones de acción"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
            }
        """)
        layout = QHBoxLayout(frame)
        
        btn_export = QPushButton("🚀 Exportar Reporte")
        btn_export.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        btn_export.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4caf50, stop:1 #2e7d32);
                color: white;
                border: 2px solid #1b5e20;
                border-radius: 15px;
                padding: 15px 30px;
                min-width: 200px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5cb860, stop:1 #3d8b40);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d8b40, stop:1 #2e572c);
            }
        """)
        btn_export.clicked.connect(self.iniciar_exportacion)
        
        layout.addStretch()
        layout.addWidget(btn_export)
        layout.addStretch()
        
        return frame

    def update_data(self, data_context, entrevista_id):
        """Actualizar datos para exportación"""
        self.data_context = data_context
        self.current_entrevista_id = entrevista_id

    def iniciar_exportacion(self):
        """Iniciar proceso de exportación"""
        if not self.current_entrevista_id:
            QMessageBox.warning(self, "Advertencia", "Selecciona una entrevista primero")
            return

        # Obtener opciones
        options = {
            'format': 'zip' if self.format_zip.isChecked() else 'pdf',
            'global_chart': self.chk_global.isChecked(),
            'individual_charts': self.chk_individual.isChecked(),
            'data_json': self.chk_data.isChecked(),
            'statistics': self.chk_stats.isChecked()
        }

        # Mostrar progreso
        self.progress_frame.show()
        self.progress_bar.setValue(0)

        # Iniciar worker
        self.worker = ExportWorker(self.data_context, self.current_entrevista_id, options)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.exportacion_completada)
        self.worker.error.connect(self.exportacion_error)
        self.worker.start()

    def exportacion_completada(self, file_path):
        """Manejar exportación completada"""
        self.progress_label.setText("Exportación completada ✅")
        
        # Preguntar dónde guardar
        default_name = f"reporte_{self.current_entrevista_id}_{datetime.now().strftime('%Y%m%d_%H%M')}.zip"
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Reporte", default_name, "ZIP Files (*.zip)"
        )
        
        if save_path:
            try:
                # Mover archivo temporal a ubicación seleccionada
                import shutil
                shutil.move(file_path, save_path)
                QMessageBox.information(self, "Éxito", f"Reporte exportado a:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error guardando archivo: {str(e)}")
        
        self.progress_frame.hide()

    def exportacion_error(self, error_msg):
        """Manejar error en exportación"""
        self.progress_label.setText("Error en exportación ❌")
        QMessageBox.critical(self, "Error", f"Error exportando reporte:\n{error_msg}")
        self.progress_frame.hide()