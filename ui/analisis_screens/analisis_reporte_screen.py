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
    """Pantalla para mostrar reportes básicos de análisis de emociones"""
    def __init__(self, logger=None, data_context=None, parent=None):
        super().__init__(parent)
        self.logger = logger or logging.getLogger(__name__)
        self.parent_window = parent
        self.data_context = data_context or {}
        self.resultados_dir = Path("data/resultados")
        self.entrevistas_disponibles = []
        self.fragmentos_data = []
        self.setup_ui()
        self.cargar_entrevistas()

    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 20, 30, 20)

        # 🔸 Header de la pantalla
        header_frame = self.create_header_frame()
        main_layout.addWidget(header_frame)

        # 🔸 Panel de selección de entrevista
        selection_frame = self.create_selection_frame()
        main_layout.addWidget(selection_frame)

        # 🔸 Contenido principal con splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background: #4caf50;
                width: 3px;
                border-radius: 1px;
            }
            QSplitter::handle:hover {
                background: #388e3c;
            }
        """)

        # Panel izquierdo - Tabla de resultados
        left_panel = self.create_results_panel()
        splitter.addWidget(left_panel)

        # Panel derecho - Resumen y estadísticas
        right_panel = self.create_summary_panel()
        splitter.addWidget(right_panel)

        # Configurar proporciones del splitter
        splitter.setSizes([600, 400])
        main_layout.addWidget(splitter, stretch=1)

        # 🔸 Panel inferior - Acciones
        action_frame = self.create_action_frame()
        main_layout.addWidget(action_frame)

    def create_header_frame(self):
        """Crear el header de la pantalla"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(76, 175, 80, 0.1),
                    stop:1 rgba(76, 175, 80, 0.05));
                border-radius: 20px;
                border: 2px solid rgba(76, 175, 80, 0.3);
                padding: 20px;
            }
            QLabel {
                color: #000000;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(10)

        # Título
        title = QLabel("📊 Reporte de Análisis de Emociones")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)

        # Descripción
        desc = QLabel("Revise los resultados del análisis de emociones por fragmento y entrevista")
        desc.setFont(QFont("Segoe UI", 12))
        desc.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(desc)

        return header_frame

    def create_selection_frame(self):
        """Crear panel de selección de entrevista"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                border: 2px solid #c8e6c9;
                padding: 15px;
            }
            QLabel {
                color: #000000;
            }
        """)
        layout = QHBoxLayout(frame)

        # Label
        label = QLabel("📋 Seleccionar Entrevista:")
        label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(label)

        # ComboBox para entrevistas
        self.entrevista_combo = QComboBox()
        self.entrevista_combo.setFont(QFont("Segoe UI", 11))
        self.entrevista_combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: 2px solid #4caf50;
                border-radius: 8px;
                padding: 8px 12px;
                color: #000000;
                min-width: 250px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #4caf50;
                margin-right: 10px;
            }
        """)
        self.entrevista_combo.currentTextChanged.connect(self.on_entrevista_selected)
        layout.addWidget(self.entrevista_combo)

        # Botón actualizar
        btn_refresh = QPushButton("🔄 Actualizar Lista")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4caf50, stop:1 #388e3c);
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5cb860, stop:1 #4caf50);
            }
        """)
        btn_refresh.clicked.connect(self.cargar_entrevistas)
        layout.addWidget(btn_refresh)

        layout.addStretch()

        return frame

    def create_results_panel(self):
        """Crear panel de tabla de resultados"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                border: 2px solid #c8e6c9;
            }
            QLabel {
                color: #000000;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header del panel
        panel_header = QLabel("📋 Resultados por Fragmento")
        panel_header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        panel_header.setStyleSheet("margin-bottom: 10px;")
        layout.addWidget(panel_header)

        # Tabla de resultados
        self.resultados_table = QTableWidget()
        self.resultados_table.setColumnCount(6)
        self.resultados_table.setHorizontalHeaderLabels([
            "🎬 Fragmento", "😊 Emoción Dominante", "📊 Confianza", 
            "🖼️ Frames", "⏱️ Duración", "📅 Fecha Análisis"
        ])
        
        # Configurar headers
        self.resultados_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.resultados_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.resultados_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.resultados_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.resultados_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.resultados_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.resultados_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.resultados_table.setAlternatingRowColors(True)
        self.resultados_table.clicked.connect(self.on_fragmento_selected)
        
        self.resultados_table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #c8e6c9;
                border-radius: 10px;
                gridline-color: #e8f5e9;
                selection-background-color: #c8e6c9;
                color: #000000;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e8f5e9;
                color: #000000;
            }
            QTableWidget::item:selected {
                background: #a5d6a7;
                color: #000000;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e8f5e9, stop:1 #c8e6c9);
                color: #000000;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-right: 1px solid #a5d6a7;
            }
        """)
        layout.addWidget(self.resultados_table)

        return panel

    def create_summary_panel(self):
        """Crear panel de resumen y estadísticas"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                border: 2px solid #c8e6c9;
            }
            QLabel {
                color: #000000;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header del panel
        panel_header = QLabel("📈 Resumen General")
        panel_header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        panel_header.setStyleSheet("margin-bottom: 10px;")
        layout.addWidget(panel_header)

        # Estadísticas generales
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background: #f1f8e9;
                border-radius: 10px;
                border: 1px solid #c8e6c9;
                padding: 15px;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        
        stats_header = QLabel("📊 Estadísticas de la Entrevista")
        stats_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        stats_header.setStyleSheet("margin-bottom: 10px;")
        stats_layout.addWidget(stats_header)
        
        self.stats_info = QLabel("Seleccione una entrevista para ver las estadísticas")
        self.stats_info.setFont(QFont("Segoe UI", 10))
        self.stats_info.setStyleSheet("line-height: 1.4;")
        self.stats_info.setWordWrap(True)
        stats_layout.addWidget(self.stats_info)
        
        layout.addWidget(stats_frame)

        # Distribución de emociones
        emotions_frame = QFrame()
        emotions_frame.setStyleSheet("""
            QFrame {
                background: #e8f5e9;
                border-radius: 10px;
                border: 1px solid #a5d6a7;
                padding: 15px;
            }
        """)
        emotions_layout = QVBoxLayout(emotions_frame)
        
        emotions_header = QLabel("😊 Distribución de Emociones")
        emotions_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        emotions_header.setStyleSheet("margin-bottom: 10px;")
        emotions_layout.addWidget(emotions_header)
        
        self.emotions_info = QLabel("No hay datos de emociones disponibles")
        self.emotions_info.setFont(QFont("Segoe UI", 10))
        self.emotions_info.setStyleSheet("line-height: 1.4;")
        self.emotions_info.setWordWrap(True)
        emotions_layout.addWidget(self.emotions_info)
        
        layout.addWidget(emotions_frame)

        # Detalles del fragmento seleccionado
        detail_frame = QFrame()
        detail_frame.setStyleSheet("""
            QFrame {
                background: #e3f2fd;
                border-radius: 10px;
                border: 1px solid #90caf9;
                padding: 15px;
            }
        """)
        detail_layout = QVBoxLayout(detail_frame)
        
        detail_header = QLabel("🔍 Detalles del Fragmento")
        detail_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        detail_header.setStyleSheet("margin-bottom: 10px;")
        detail_layout.addWidget(detail_header)
        
        self.detail_info = QLabel("Seleccione un fragmento para ver detalles específicos")
        self.detail_info.setFont(QFont("Segoe UI", 10))
        self.detail_info.setStyleSheet("line-height: 1.4;")
        self.detail_info.setWordWrap(True)
        detail_layout.addWidget(self.detail_info)
        
        layout.addWidget(detail_frame)

        layout.addStretch()
        return panel

    def create_action_frame(self):
        """Crear frame con botones de acción"""
        action_frame = QFrame()
        action_frame.setStyleSheet("""
            QFrame {
                background: rgba(232, 245, 233, 0.8);
                border-radius: 15px;
                border: 1px solid #a5d6a7;
                padding: 15px;
            }
            QLabel {
                color: #000000;
            }
        """)
        layout = QHBoxLayout(action_frame)
        
        # Información de resumen
        self.summary_label = QLabel("Seleccione una entrevista para ver el reporte de análisis")
        self.summary_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.summary_label)
        
        layout.addStretch()
        
        # Botones de acción
        self.btn_export = QPushButton("📤 Exportar Reporte")
        self.btn_export.setEnabled(False)
        self.btn_export.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2196F3, stop:1 #1976D2);
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:disabled {
                background: #cccccc;
                color: #666666;
            }
            QPushButton:hover:enabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #42A5F5, stop:1 #1E88E5);
            }
        """)
        self.btn_export.clicked.connect(self.exportar_reporte)
        layout.addWidget(self.btn_export)

        return action_frame

    def cargar_entrevistas(self):
        """Cargar entrevistas que tienen resultados disponibles"""
        try:
            if not self.resultados_dir.exists():
                self.entrevista_combo.clear()
                self.summary_label.setText("❌ No existe el directorio de resultados")
                return

            # Buscar carpetas de entrevistas
            self.entrevistas_disponibles = [d for d in self.resultados_dir.iterdir() if d.is_dir()]
            
            self.entrevista_combo.clear()
            self.entrevista_combo.addItem("-- Seleccione una entrevista --")
            
            for entrevista in self.entrevistas_disponibles:
                resultados = list(entrevista.glob("*.json"))
                if resultados:
                    self.entrevista_combo.addItem(
                        f"{entrevista.name} ({len(resultados)} análisis)"
                    )

            if len(self.entrevistas_disponibles) == 0:
                self.summary_label.setText("ℹ️ No hay entrevistas con análisis disponibles")
            else:
                self.summary_label.setText(f"✅ {len(self.entrevistas_disponibles)} entrevistas con análisis encontradas")

        except Exception as e:
            self.mostrar_error(f"Error al cargar entrevistas: {str(e)}")

    def on_entrevista_selected(self, texto):
        """Manejar selección de entrevista"""
        if texto == "-- Seleccione una entrevista --" or not texto:
            self.fragmentos_data = []
            self.actualizar_tabla_resultados()
            self.actualizar_resumen()
            self.btn_export.setEnabled(False)
            return

        # Extraer ID de entrevista del texto
        entrevista_id = texto.split(' ')[0]
        self.cargar_resultados_entrevista(entrevista_id)
        self.btn_export.setEnabled(True)

    def cargar_resultados_entrevista(self, entrevista_id):
        """Cargar resultados de análisis para una entrevista específica"""
        try:
            entrevista_dir = self.resultados_dir / entrevista_id
            if not entrevista_dir.exists():
                self.mostrar_error(f"No se encuentra la carpeta de resultados para {entrevista_id}")
                return

            resultados_files = list(entrevista_dir.glob("*.json"))
            self.fragmentos_data = []

            for json_file in resultados_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    fragmento_info = data['fragmento']
                    analisis_info = data['analisis']
                    resumen = analisis_info.get('resumen_emociones', {})
                    
                    # Crear información del fragmento
                    fragmento_data = {
                        'file_path': json_file,
                        'name': fragmento_info.get('nombre', 'N/A'),
                        'entrevista_id': fragmento_info.get('entrevista_id', 'N/A'),
                        'pregunta_id': fragmento_info.get('pregunta_id', 'N/A'),
                        'dominant_emotion': resumen.get('dominant_emotion', 'N/A'),
                        'confidence': resumen.get('confidence', 0),
                        'total_frames': analisis_info.get('total_frames_analizados', 0),
                        'duration': fragmento_info.get('duration', 'N/A'),
                        'fecha_analisis': analisis_info.get('fecha_analisis', 'N/A'),
                        'avg_intensities': resumen.get('avg_intensities', {}),
                        'modelo_utilizado': analisis_info.get('modelo_utilizado', 'N/A')
                    }
                    
                    self.fragmentos_data.append(fragmento_data)
                    
                except Exception as e:
                    self.logger.error(f"Error procesando {json_file}: {str(e)}")
                    continue

            self.actualizar_tabla_resultados()
            self.actualizar_resumen()

        except Exception as e:
            self.mostrar_error(f"Error al cargar resultados: {str(e)}")

    def actualizar_tabla_resultados(self):
        """Actualizar la tabla con los resultados de los fragmentos"""
        self.resultados_table.setRowCount(len(self.fragmentos_data))
        
        for row, frag in enumerate(self.fragmentos_data):
            # Nombre del fragmento
            name_item = QTableWidgetItem(frag['name'])
            name_item.setData(Qt.UserRole, row)
            
            # Emoción dominante
            emotion_item = QTableWidgetItem(frag['dominant_emotion'])
            
            # Confianza
            confidence_item = QTableWidgetItem(f"{frag['confidence']:.3f}")
            
            # Frames analizados
            frames_item = QTableWidgetItem(str(frag['total_frames']))
            
            # Duración
            duration_item = QTableWidgetItem(frag.get('duration', 'N/A'))
            
            # Fecha de análisis
            fecha = frag.get('fecha_analisis', 'N/A')
            if fecha != 'N/A':
                try:
                    fecha_dt = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
                    fecha_str = fecha_dt.strftime("%Y-%m-%d %H:%M")
                except:
                    fecha_str = fecha
            else:
                fecha_str = 'N/A'
            fecha_item = QTableWidgetItem(fecha_str)
            
            self.resultados_table.setItem(row, 0, name_item)
            self.resultados_table.setItem(row, 1, emotion_item)
            self.resultados_table.setItem(row, 2, confidence_item)
            self.resultados_table.setItem(row, 3, frames_item)
            self.resultados_table.setItem(row, 4, duration_item)
            self.resultados_table.setItem(row, 5, fecha_item)

    def actualizar_resumen(self):
        """Actualizar el resumen y estadísticas"""
        if not self.fragmentos_data:
            self.stats_info.setText("No hay datos disponibles para mostrar")
            self.emotions_info.setText("No hay datos de emociones disponibles")
            self.detail_info.setText("Seleccione un fragmento para ver detalles específicos")
            return

        # Estadísticas generales
        total_fragmentos = len(self.fragmentos_data)
        total_frames = sum(frag['total_frames'] for frag in self.fragmentos_data)
        avg_confidence = sum(frag['confidence'] for frag in self.fragmentos_data) / total_fragmentos
        
        stats_text = f"""
        • <b>Total de fragmentos analizados:</b> {total_fragmentos}<br>
        • <b>Total de frames procesados:</b> {total_frames}<br>
        • <b>Confianza promedio:</b> {avg_confidence:.3f}<br>
        • <b>Modelo utilizado:</b> {self.fragmentos_data[0].get('modelo_utilizado', 'N/A')}
        """
        self.stats_info.setText(stats_text)

        # Distribución de emociones
        emociones = {}
        for frag in self.fragmentos_data:
            emocion = frag['dominant_emotion']
            emociones[emocion] = emociones.get(emocion, 0) + 1
        
        emotions_text = "<b>Distribución de emociones dominantes:</b><br>"
        for emocion, count in sorted(emociones.items(), key=lambda x: x[1], reverse=True):
            porcentaje = (count / total_fragmentos) * 100
            emotions_text += f"• {emocion}: {count} ({porcentaje:.1f}%)<br>"
        
        self.emotions_info.setText(emotions_text)

        # Actualizar resumen inferior
        self.summary_label.setText(
            f"📊 {total_fragmentos} fragmentos analizados | "
            f"😊 {len(emociones)} emociones detectadas | "
            f"📈 Confianza promedio: {avg_confidence:.3f}"
        )

    def on_fragmento_selected(self, index):
        """Manejar selección de fragmento en la tabla"""
        row = index.row()
        if 0 <= row < len(self.fragmentos_data):
            fragmento = self.fragmentos_data[row]
            self.mostrar_detalles_fragmento(fragmento)

    def mostrar_detalles_fragmento(self, fragmento):
        """Mostrar detalles específicos del fragmento seleccionado"""
        detalles_text = f"""
        <b>🎬 Fragmento:</b> {fragmento['name']}<br>
        <b>😊 Emoción dominante:</b> {fragmento['dominant_emotion']}<br>
        <b>📊 Confianza:</b> {fragmento['confidence']:.3f}<br>
        <b>🖼️ Frames analizados:</b> {fragmento['total_frames']}<br>
        <b>⏱️ Duración:</b> {fragmento.get('duration', 'N/A')}<br>
        <b>🆔 Entrevista:</b> {fragmento['entrevista_id']}<br>
        <b>❓ Pregunta ID:</b> {fragmento['pregunta_id']}<br>
        <b>🤖 Modelo:</b> {fragmento.get('modelo_utilizado', 'N/A')}<br>
        <b>📅 Fecha análisis:</b> {fragmento.get('fecha_analisis', 'N/A')}
        """
        
        # Agregar intensidades promedio si están disponibles
        if fragmento.get('avg_intensities'):
            detalles_text += "<br><b>📈 Intensidades promedio:</b><br>"
            for emocion, intensidad in fragmento['avg_intensities'].items():
                detalles_text += f"• {emocion}: {intensidad:.3f}<br>"
        
        self.detail_info.setText(detalles_text)

    def exportar_reporte(self):
        """Exportar reporte a formato JSON"""
        if not self.fragmentos_data:
            self.mostrar_advertencia("No hay datos para exportar")
            return

        try:
            # Crear nombre de archivo
            entrevista_id = self.fragmentos_data[0]['entrevista_id']
            fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reporte_{entrevista_id}_{fecha_actual}.json"
            
            # Obtener ruta de guardado
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Exportar Reporte",
                filename,
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                # Preparar datos para exportación
                reporte_data = {
                    'metadata': {
                        'entrevista_id': entrevista_id,
                        'fecha_generacion': datetime.now().isoformat(),
                        'total_fragmentos': len(self.fragmentos_data),
                        'modelo_utilizado': self.fragmentos_data[0].get('modelo_utilizado', 'N/A')
                    },
                    'resumen_general': self.generar_resumen_exportacion(),
                    'resultados_detallados': self.fragmentos_data
                }
                
                # Guardar archivo
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(reporte_data, f, ensure_ascii=False, indent=2)
                
                self.mostrar_info(f"✅ Reporte exportado exitosamente: {Path(file_path).name}")
                
        except Exception as e:
            self.mostrar_error(f"Error al exportar reporte: {str(e)}")

    def generar_resumen_exportacion(self):
        """Generar resumen para exportación"""
        emociones = {}
        total_confidence = 0
        
        for frag in self.fragmentos_data:
            emocion = frag['dominant_emotion']
            emociones[emocion] = emociones.get(emocion, 0) + 1
            total_confidence += frag['confidence']
        
        return {
            'distribucion_emociones': emociones,
            'confianza_promedio': total_confidence / len(self.fragmentos_data) if self.fragmentos_data else 0,
            'total_frames_analizados': sum(frag['total_frames'] for frag in self.fragmentos_data)
        }

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def mostrar_error(self, msg):
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Error")
        msgbox.setText(msg)
        msgbox.setIcon(QMessageBox.Critical)
        msgbox.setStyleSheet("QLabel { color: #000000; background-color: white; }")
        msgbox.exec()
        self.logger.error(msg)

    def mostrar_advertencia(self, msg):
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Advertencia")
        msgbox.setText(msg)
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setStyleSheet("QLabel { color: #000000; background-color: white; }")
        msgbox.exec()
        self.logger.warning(msg)

    def mostrar_info(self, msg):
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Información")
        msgbox.setText(msg)
        msgbox.setIcon(QMessageBox.Information)
        msgbox.setStyleSheet("QLabel { color: #000000; background-color: white; }")
        msgbox.exec()
        self.logger.info(msg)