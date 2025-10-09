import logging
from pathlib import Path
import json
import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QGridLayout, QComboBox, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from ..utils.styles import ColorPalette

class ResumenScreen(QWidget):
    def __init__(self, logger=None, data_context=None, parent=None):
        super().__init__(parent)
        self.logger = logger or logging.getLogger(__name__)
        self.data_context = data_context or {}
        self.current_entrevista_id = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title = QLabel("📊 Resumen Global - Gráficos Araña")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #2e7d32;
                background: rgba(255, 255, 255, 0.9);
                padding: 15px;
                border-radius: 15px;
                border: 2px solid #4caf50;
            }
        """)
        layout.addWidget(title)

        # Contenedor scrollable para múltiples gráficos
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(25)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        
        scroll_area.setWidget(self.scroll_content)
        layout.addWidget(scroll_area)

        # Placeholder inicial
        self.placeholder_label = QLabel("🌱 Selecciona una entrevista para ver los gráficos de resumen")
        self.placeholder_label.setFont(QFont("Arial", 14, QFont.Weight.Medium))
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setStyleSheet("""
            QLabel {
                color: #666;
                padding: 40px;
                background: rgba(255, 255, 255, 0.8);
                border-radius: 20px;
                border: 2px dashed #ccc;
            }
        """)
        self.scroll_layout.addWidget(self.placeholder_label)

    def update_data(self, data_context, entrevista_id):
        """Actualizar datos y mostrar gráficos"""
        self.data_context = data_context
        self.current_entrevista_id = entrevista_id
        
        # Limpiar layout anterior
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        if not entrevista_id or entrevista_id not in data_context.get("por_entrevista", {}):
            self.show_placeholder("No hay datos disponibles para esta entrevista")
            return

        self.mostrar_graficos_resumen()

    def mostrar_graficos_resumen(self):
        """Mostrar gráficos de resumen para la entrevista seleccionada"""
        try:
            entrevista_data = self.data_context["por_entrevista"][self.current_entrevista_id]
            
            # 1. Gráfico araña de promedios globales
            self.crear_grafico_global(entrevista_data)
            
            # 2. Gráficos individuales por pregunta
            self.crear_graficos_por_pregunta(entrevista_data)
            
        except Exception as e:
            self.logger.error(f"Error mostrando gráficos de resumen: {str(e)}")
            self.show_placeholder(f"Error al generar gráficos: {str(e)}")

    def crear_grafico_global(self, entrevista_data):
        """Crear gráfico araña con promedios globales - CORREGIDO"""
        # Calcular promedios de todas las preguntas
        emociones = ["angry", "contempt", "disgust", "fear", "happy", "surprise", "sad"]
        promedios = {emo: 0 for emo in emociones}
        count = 0
        
        for pregunta_id, datos in entrevista_data.items():
            intensidad = datos.get("intensidad", {})
            for emo in emociones:
                promedios[emo] += intensidad.get(emo, 0)
            count += 1
        
        if count > 0:
            for emo in emociones:
                promedios[emo] /= count

        # Crear gráfico araña
        fig = Figure(figsize=(10, 8), facecolor='#f8fff8')
        canvas = FigureCanvas(fig)
        
        # Traducción de emociones al español
        emociones_es = {
            "angry": "Enojo",
            "contempt": "Desprecio", 
            "disgust": "Disgusto",
            "fear": "Miedo",
            "happy": "Felicidad",
            "surprise": "Sorpresa",
            "sad": "Tristeza"
        }
        
        categorias = [emociones_es[emo] for emo in emociones]
        valores = [promedios[emo] for emo in emociones]
        
        # CORRECCIÓN: Cerrar el polígono correctamente
        # Necesitamos el mismo número de ángulos que de valores
        num_vars = len(categorias)
        
        # Calcular ángulos para cada eje
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        
        # Cerrar el polígono repitiendo el primer valor al final
        valores_cerrado = valores + valores[:1]
        angles_cerrado = angles + angles[:1]
        
        ax = fig.add_subplot(111, polar=True)
        ax.plot(angles_cerrado, valores_cerrado, 'o-', linewidth=2, label='Promedio Global', 
                color='#2e7d32', markersize=8)
        ax.fill(angles_cerrado, valores_cerrado, alpha=0.25, color='#4caf50')
        
        # Configurar ejes
        ax.set_xticks(angles)
        ax.set_xticklabels(categorias, fontsize=11)
        
        # Establecer límites del gráfico
        y_max = max(valores_cerrado) * 1.2 if max(valores_cerrado) > 0 else 0.2
        ax.set_ylim(0, y_max)
        ax.set_yticks(np.linspace(0, y_max, 5))
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('#f1f8e9')
        
        plt.title(f'Resumen Emocional Global\nEntrevista {self.current_entrevista_id}', 
                size=14, pad=20, color='#2e572c', weight='bold')

        # Frame para el gráfico (CORREGIDO: sin box-shadow)
        graph_frame = QFrame()
        graph_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                border: 2px solid #c8e6c9;
                padding: 15px;
            }
        """)
        graph_layout = QVBoxLayout(graph_frame)
        
        title_label = QLabel("🌐 Gráfico Araña - Promedio Global")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1b5e20; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        graph_layout.addWidget(title_label)
        
        graph_layout.addWidget(canvas)
        self.scroll_layout.addWidget(graph_frame)
    
    
    def crear_graficos_por_pregunta(self, entrevista_data):
        """Crear gráficos individuales para cada pregunta - CORREGIDO"""
        emociones_es = {
            "angry": "Enojo", "contempt": "Desprecio", "disgust": "Disgusto", "fear": "Miedo",
            "happy": "Felicidad", "surprise": "Sorpresa", "sad": "Tristeza"
        }
        
        emociones_en = list(emociones_es.keys())
        categorias = list(emociones_es.values())
        
        # Layout de grid para los gráficos individuales
        grid_frame = QFrame()
        grid_frame.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
            }
        """)
        grid_layout = QGridLayout(grid_frame)
        grid_layout.setSpacing(20)
        
        title_label = QLabel("📋 Gráficos por Pregunta Individual")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1b5e20; padding: 15px;")
        title_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(title_label)
        
        # Ordenar preguntas numéricamente
        preguntas_ordenadas = sorted(
            entrevista_data.items(), 
            key=lambda x: int(x[0]) if x[0].isdigit() else 0
        )
        
        for i, (pregunta_id, datos) in enumerate(preguntas_ordenadas):
            row = i // 2
            col = i % 2
            
            # Crear gráfico individual
            fig = Figure(figsize=(6, 5), facecolor='#f8fff8')
            canvas = FigureCanvas(fig)
            
            intensidad = datos.get("intensidad", {})
            valores = [intensidad.get(emo, 0) for emo in emociones_en]
            
            # CORRECCIÓN: Cerrar polígono correctamente
            num_vars = len(categorias)
            angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
            
            valores_cerrado = valores + valores[:1]
            angles_cerrado = angles + angles[:1]
            
            ax = fig.add_subplot(111, polar=True)
            ax.plot(angles_cerrado, valores_cerrado, 'o-', linewidth=2, 
                    color='#388e3c', markersize=6)
            ax.fill(angles_cerrado, valores_cerrado, alpha=0.3, color='#66bb6a')
            
            ax.set_xticks(angles)
            ax.set_xticklabels(categorias, fontsize=9)
            
            y_max = max(valores_cerrado) * 1.2 if max(valores_cerrado) > 0 else 0.2
            ax.set_ylim(0, y_max)
            ax.set_yticks([])
            ax.grid(True, alpha=0.3)
            ax.set_facecolor('#f1f8e9')
            
            nota = datos.get("nota", "Sin comentarios")
            plt.title(f'Pregunta {pregunta_id}', 
                    size=10, pad=15, color='#2e572c')
            
            # Frame individual (CORREGIDO: sin box-shadow)
            individual_frame = QFrame()
            individual_frame.setStyleSheet("""
                QFrame {
                    background: rgba(255, 255, 255, 0.9);
                    border-radius: 15px;
                    border: 2px solid #a5d6a7;
                    padding: 12px;
                }
            """)
            individual_layout = QVBoxLayout(individual_frame)
            individual_layout.addWidget(canvas)
            
            grid_layout.addWidget(individual_frame, row, col)
        
        self.scroll_layout.addWidget(grid_frame)
    

    def show_placeholder(self, message):
        """Mostrar mensaje placeholder"""
        self.placeholder_label = QLabel(f"🌱 {message}")
        self.placeholder_label.setFont(QFont("Arial", 14, QFont.Weight.Medium))
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setStyleSheet("""
            QLabel {
                color: #666;
                padding: 40px;
                background: rgba(255, 255, 255, 0.8);
                border-radius: 20px;
                border: 2px dashed #ccc;
            }
        """)
        self.scroll_layout.addWidget(self.placeholder_label)