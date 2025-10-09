import logging
from pathlib import Path
import json
import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QGridLayout, QComboBox, QPushButton, QSplitter, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from ..utils.styles import ColorPalette

class DetalleScreen(QWidget):
    def __init__(self, logger=None, data_context=None, parent=None):
        super().__init__(parent)
        self.logger = logger or logging.getLogger(__name__)
        self.data_context = data_context or {}
        self.current_entrevista_id = None
        self.current_pregunta_id = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Panel izquierdo - Selector de preguntas
        left_panel = self.crear_panel_selector()
        main_layout.addWidget(left_panel, 1)

        # Panel derecho - Visualización de detalles
        right_panel = self.crear_panel_detalle()
        main_layout.addWidget(right_panel, 2)

    def crear_panel_selector(self):
        """Crear panel para seleccionar preguntas"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                border: 2px solid #c8e6c9;
                padding: 20px;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)

        # Título
        title = QLabel("📋 Preguntas")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #1b5e20; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Lista de preguntas (scrollable)
        self.preguntas_scroll = QScrollArea()
        self.preguntas_scroll.setWidgetResizable(True)
        self.preguntas_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.preguntas_widget = QWidget()
        self.preguntas_layout = QVBoxLayout(self.preguntas_widget)
        self.preguntas_layout.setSpacing(10)
        self.preguntas_layout.setAlignment(Qt.AlignTop)
        
        self.preguntas_scroll.setWidget(self.preguntas_widget)
        layout.addWidget(self.preguntas_scroll)

        return panel

    def crear_panel_detalle(self):
        """Crear panel de visualización de detalles"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                border: 2px solid #c8e6c9;
                padding: 20px;
            }
        """)
        self.detalle_layout = QVBoxLayout(panel)
        self.detalle_layout.setSpacing(20)

        # Placeholder inicial
        self.detalle_placeholder = QLabel("🔍 Selecciona una pregunta para ver el análisis detallado")
        self.detalle_placeholder.setFont(QFont("Arial", 14, QFont.Weight.Medium))
        self.detalle_placeholder.setAlignment(Qt.AlignCenter)
        self.detalle_placeholder.setStyleSheet("""
            QLabel {
                color: #666;
                padding: 60px;
                background: rgba(248, 255, 248, 0.8);
                border-radius: 20px;
                border: 2px dashed #ccc;
            }
        """)
        self.detalle_layout.addWidget(self.detalle_placeholder)

        return panel

    def update_data(self, data_context, entrevista_id):
        """Actualizar datos y mostrar selector de preguntas - CORREGIDO"""
        self.data_context = data_context
        self.current_entrevista_id = entrevista_id
        
        # Limpiar layout de preguntas
        for i in reversed(range(self.preguntas_layout.count())):
            widget = self.preguntas_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        if not entrevista_id or entrevista_id not in data_context.get("por_entrevista", {}):
            no_data_label = QLabel("No hay preguntas disponibles")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("color: #666; padding: 20px;")
            self.preguntas_layout.addWidget(no_data_label)
            return

        # Crear botones para cada pregunta - CORREGIDO: ordenar numéricamente
        entrevista_data = data_context["por_entrevista"][entrevista_id]
        
        # Ordenar preguntas numéricamente
        preguntas_ordenadas = sorted(
            entrevista_data.items(), 
            key=lambda x: int(x[0]) if x[0].isdigit() else 0
        )
        
        for pregunta_id, datos in preguntas_ordenadas:
            self.crear_boton_pregunta(pregunta_id, datos)

    def crear_boton_pregunta(self, pregunta_id, datos):
        """Crear botón para una pregunta específica - CORREGIDO"""
        btn = QPushButton()
        btn.setFixedHeight(80)
        btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(232, 245, 233, 0.9),
                    stop:1 rgba(200, 230, 201, 0.9));
                border: 2px solid #a5d6a7;
                border-radius: 15px;
                padding: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(200, 230, 201, 0.95),
                    stop:1 rgba(165, 214, 167, 0.95));
                border: 2px solid #4caf50;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(165, 214, 167, 0.9),
                    stop:1 rgba(129, 199, 132, 0.9));
            }
        """)
        
        # Contenido del botón - CORREGIDO: usar datos reales
        nota = datos.get("nota", "Sin comentarios")
        emocion_dominante = datos.get("emocion_dominante", "N/A")
        confidence = datos.get("confidence", 0)
        
        layout = QVBoxLayout()
        
        # Línea 1: Pregunta ID y emoción dominante
        top_layout = QHBoxLayout()
        preg_label = QLabel(f"Pregunta {pregunta_id}")
        preg_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        preg_label.setStyleSheet("color: #2e7d32;")
        
        emocion_label = QLabel(f"🎭 {emocion_dominante} ({confidence:.3f})")
        emocion_label.setFont(QFont("Segoe UI", 10))
        emocion_label.setStyleSheet("color: #555;")
        
        top_layout.addWidget(preg_label)
        top_layout.addStretch()
        top_layout.addWidget(emocion_label)
        layout.addLayout(top_layout)
        
        # Línea 2: Comentario truncado
        nota_label = QLabel(nota[:50] + "..." if len(nota) > 50 else nota)
        nota_label.setFont(QFont("Segoe UI", 9))
        nota_label.setStyleSheet("color: #666;")
        nota_label.setWordWrap(True)
        layout.addWidget(nota_label)
        
        btn.setLayout(layout)
        
        # CORRECCIÓN: Lambda correcta
        btn.clicked.connect(lambda checked, pid=pregunta_id: self.mostrar_detalle_pregunta(pid))
        
        self.preguntas_layout.addWidget(btn)
        
        


    def mostrar_detalle_pregunta(self, pregunta_id):
        """Mostrar detalles completos de una pregunta"""
        self.current_pregunta_id = pregunta_id
        
        # Limpiar panel de detalle
        for i in reversed(range(self.detalle_layout.count())):
            widget = self.detalle_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        if not self.current_entrevista_id:
            return
            
        datos = self.data_context["por_entrevista"][self.current_entrevista_id].get(pregunta_id, {})
        
        # Título
        title = QLabel(f"📊 Análisis Detallado - Pregunta {pregunta_id}")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #1b5e20; padding: 15px;")
        title.setAlignment(Qt.AlignCenter)
        self.detalle_layout.addWidget(title)
        
        # Información de la pregunta
        info_frame = self.crear_info_pregunta(datos)
        self.detalle_layout.addWidget(info_frame)
        
        # Gráfico araña
        graph_frame = self.crear_grafico_detalle(datos, pregunta_id)
        self.detalle_layout.addWidget(graph_frame)

    def crear_info_pregunta(self, datos):
        """Crear frame con información de la pregunta"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: rgba(248, 255, 248, 0.9);
                border-radius: 15px;
                border: 2px solid #c8e6c9;
                padding: 20px;
            }
        """)
        layout = QVBoxLayout(frame)
        
        # Comentario/nota
        nota = datos.get("nota", "Sin comentarios")
        nota_label = QLabel(f"📝 Comentario: {nota}")
        nota_label.setFont(QFont("Segoe UI", 12))
        nota_label.setStyleSheet("color: #2e572c; padding: 5px;")
        nota_label.setWordWrap(True)
        layout.addWidget(nota_label)
        
        # Tiempos
        inicio = datos.get("inicio", 0)
        fin = datos.get("fin", 0)
        tiempo_label = QLabel(f"⏱️ Duración: {inicio}s - {fin}s ({(fin-inicio):.1f}s)")
        tiempo_label.setFont(QFont("Segoe UI", 11))
        tiempo_label.setStyleSheet("color: #555; padding: 5px;")
        layout.addWidget(tiempo_label)
        
        # Emoción dominante
        intensidad = datos.get("intensidad", {})
        if intensidad:
            emocion_dom = max(intensidad.items(), key=lambda x: x[1])
            emocion_label = QLabel(f"🎯 Emoción dominante: {emocion_dom[0]} ({emocion_dom[1]:.3f})")
            emocion_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
            emocion_label.setStyleSheet("color: #d32f2f; padding: 5px;")
            layout.addWidget(emocion_label)
        
        return frame

    def crear_grafico_detalle(self, datos, pregunta_id):
        """Crear gráfico araña detallado"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                border: 2px solid #c8e6c9;
                padding: 20px;
            }
        """)
        layout = QVBoxLayout(frame)
        
        # Título del gráfico
        graph_title = QLabel(f"🕸️ Perfil Emocional - Pregunta {pregunta_id}")
        graph_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        graph_title.setStyleSheet("color: #1b5e20; padding: 10px;")
        graph_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(graph_title)
        
        # Crear gráfico
        fig = Figure(figsize=(10, 8), facecolor='#f8fff8')
        canvas = FigureCanvas(fig)
        
        emociones_es = {
            "angry": "Enojo", "disgust": "Disgusto", "fear": "Miedo",
            "happy": "Felicidad", "surprise": "Sorpresa", "sad": "Tristeza",
            "contempt": "Desprecio"
        }
        
        emociones_en = list(emociones_es.keys())
        categorias = list(emociones_es.values())
        
        intensidad = datos.get("intensidad", {})
        valores = [intensidad.get(emo, 0) for emo in emociones_en]
        
        # Cerrar polígono
        categorias_cerrado = categorias + categorias[:1]
        valores_cerrado = valores + valores[:1]
        
        ax = fig.add_subplot(111, polar=True)
        angles = np.linspace(0, 2*np.pi, len(categorias), endpoint=False).tolist()
        angles += angles[:1]
        
        # Gráfico principal
        ax.plot(angles, valores_cerrado, 'o-', linewidth=3, 
                color='#2e7d32', markersize=10, label='Intensidad')
        ax.fill(angles, valores_cerrado, alpha=0.25, color='#4caf50')
        
        # Etiquetas de valores
        for angle, valor, categoria in zip(angles[:-1], valores, categorias):
            ax.text(angle, valor + 0.02, f'{valor:.3f}', 
                   ha='center', va='bottom', fontsize=9, color='#1b5e20')
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categorias, fontsize=12)
        ax.set_ylim(0, max(valores_cerrado) * 1.3 if max(valores_cerrado) > 0 else 1)
        ax.set_yticks([])
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('#f1f8e9')
        
        plt.title('Distribución de Emociones', size=14, pad=25, 
                 color='#2e572c', weight='bold')
        
        layout.addWidget(canvas)
        return frame