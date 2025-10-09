import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTabWidget, QMessageBox,
    QHBoxLayout, QFrame, QProgressBar
)
from PySide6.QtCore import QTimer, QObject, Signal, Slot, QUrl, Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtGui import QFont
from pathlib import Path

from classes.entrevista_preguntas import EntrevistaPreguntas

# ---- Paleta de colores agrícolas ----
COLOR_PALETTE = {
    'DARK_GREEN': '#1b5e20',
    'PRIMARY_GREEN': '#2e7d32', 
    'MEDIUM_GREEN': '#388e3c',
    'LIGHT_GREEN': '#4caf50',
    'SOFT_GREEN': '#66bb6a',
    'BRIGHT_GREEN': '#81c784',
    'PALE_GREEN': '#a5d6a7',
    'MINT_GREEN': '#c8e6c9',
    'WHITE_GREEN': '#e8f5e9',
    'FOREST_GREEN': '#2e572c',
    'SPRING_GREEN': '#43a047',
    'GRASS_GREEN': '#558b2f',
    'LEAF_GREEN': '#689f38'
}

# ---- Bridge Python ↔ JS ----
class DataBridge(QObject):
    updateData = Signal(dict)
    updatePregunta = Signal(str, int)

    @Slot(int, int, int, int)
    def setValues(self, humedad, temperatura, lluvia, viento):
        self.updateData.emit({
            "humedad": humedad,
            "temperatura": temperatura,
            "lluvia": lluvia,
            "viento": viento
        })

    @Slot(str, int)
    def setPregunta(self, categoria, pregunta_idx):
        """Slot que puede ser llamado desde JS o desde otro bridge para propagar la pregunta."""
        self.updatePregunta.emit(categoria, pregunta_idx)


class IntervieweeScreen(QWidget):
    VISUAL_CATEGORIES = ["Semaforo", "Pictogramas", "Tabla"]

    def __init__(self, bridge: DataBridge):
        super().__init__()
        self.setWindowTitle("🌱 Entrevista UX - Pantalla Entrevistado")
        self.resize(1400, 900)
        
        # Aplicar paleta de colores global
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLOR_PALETTE['DARK_GREEN']}, 
                    stop:0.3 {COLOR_PALETTE['PRIMARY_GREEN']},
                    stop:0.7 {COLOR_PALETTE['LIGHT_GREEN']},
                    stop:1 {COLOR_PALETTE['SOFT_GREEN']});
                color: black;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)

        self.bridge = bridge
        self.preguntas = EntrevistaPreguntas()
        self.categorias = list(self.preguntas.preguntas.keys())
        self.categoria_idx = 0
        self.pregunta_idx = 0
        self.webviews_loaded = {}  # Track carga de webviews

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(30, 30, 30, 30)

        # Conectar señales
        self.bridge.updateData.connect(self.on_update_data)
        self.bridge.updatePregunta.connect(self.actualizar_desde_bridge)

        # Crear interfaz
        self.crear_header()
        self.crear_area_pregunta()
        self.crear_tabs_visuales()
        self.crear_footer()

        # Mostrar la primera pregunta
        QTimer.singleShot(500, self.actualizar_pregunta)  # Pequeño delay para asegurar carga

    def crear_header(self):
        """Crear encabezado con diseño agrícola"""
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(46, 125, 50, 0.9),
                    stop:0.5 rgba(56, 142, 60, 0.85),
                    stop:1 rgba(76, 175, 80, 0.8));
                border-radius: 25px;
                border: 3px solid rgba(255, 255, 255, 0.3);
                padding: 20px;
            }}
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(15)

        # Título principal
        title = QLabel("🎯 Pantalla del Entrevistado")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: white;
                background: transparent;
                padding: 10px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
        """)
        header_layout.addWidget(title)

        # Subtítulo
        subtitle = QLabel("Interfaz para visualización de prototipos durante la entrevista UX")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: #e8f5e9;
                background: rgba(255, 255, 255, 0.1);
                padding: 8px 20px;
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)
        header_layout.addWidget(subtitle)

        self.layout.addWidget(header_frame)

    def crear_area_pregunta(self):
        """Crear área para mostrar la pregunta actual"""
        pregunta_frame = QFrame()
        pregunta_frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                border: 3px solid {COLOR_PALETTE['LIGHT_GREEN']};
                padding: 25px;
            }}
        """)
        pregunta_layout = QVBoxLayout(pregunta_frame)

        # Etiqueta de categoría
        self.lbl_categoria = QLabel()
        self.lbl_categoria.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.lbl_categoria.setStyleSheet("""
            QLabel {
                color: #1b5e20;
                background: rgba(232, 245, 233, 0.8);
                padding: 8px 15px;
                border-radius: 10px;
                border: 1px solid #a5d6a7;
            }
        """)
        pregunta_layout.addWidget(self.lbl_categoria)

        # Pregunta actual
        self.lbl_pregunta = QLabel()
        self.lbl_pregunta.setWordWrap(True)
        self.lbl_pregunta.setFont(QFont("Segoe UI", 18))
        self.lbl_pregunta.setStyleSheet("""
            QLabel {
                color: black;
                background: rgba(248, 255, 248, 0.9);
                padding: 20px;
                border-radius: 15px;
                border: 2px solid #c8e6c9;
                line-height: 1.4;
            }
        """)
        pregunta_layout.addWidget(self.lbl_pregunta)

        # Barra de progreso de la entrevista
        self.progress_frame = QFrame()
        self.progress_frame.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
            }
        """)
        progress_layout = QHBoxLayout(self.progress_frame)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #c8e6c9;
                border-radius: 10px;
                text-align: center;
                background: #f1f8e9;
                height: 20px;
                color: black;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4caf50, stop:1 #2e7d32);
                border-radius: 8px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.lbl_progreso = QLabel()
        self.lbl_progreso.setFont(QFont("Segoe UI", 11))
        self.lbl_progreso.setStyleSheet("color: #555; padding: 5px;")
        progress_layout.addWidget(self.lbl_progreso)
        
        pregunta_layout.addWidget(self.progress_frame)

        self.layout.addWidget(pregunta_frame)

    def crear_tabs_visuales(self):
        """Crear tabs para los prototipos visuales"""
        self.tabs_container = QFrame()
        self.tabs_container.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
            }
        """)
        tabs_layout = QVBoxLayout(self.tabs_container)

        # Título de las tabs
        self.tabs_title = QLabel("📊 Prototipos Visuales")
        self.tabs_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.tabs_title.setStyleSheet("color: white; padding: 10px;")
        self.tabs_title.setAlignment(Qt.AlignCenter)
        tabs_layout.addWidget(self.tabs_title)

        # Widget de tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 3px solid #c8e6c9;
                border-radius: 15px;
                background: rgba(255, 255, 255, 0.98);
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a5d6a7, stop:1 #81c784);
                border: 2px solid #66bb6a;
                border-bottom: none;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                padding: 12px 20px;
                margin-right: 2px;
                color: black;
                font-weight: bold;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4caf50, stop:1 #388e3c);
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c8e6c9, stop:1 #a5d6a7);
            }
        """)

        self.webviews = {}
        self.carta_ids = ["carta-semaforo", "carta-visuales", "carta-tabla"]
        self.tab_names = ["🚦 Semáforo", "🎨 Elementos Visuales", "📋 Tabla de Datos"]

        for i, carta_id in enumerate(self.carta_ids):
            view = QWebEngineView()
            view.setStyleSheet("""
                QWebEngineView {
                    background: white;
                    border-radius: 12px;
                    border: 2px solid #e8f5e9;
                }
            """)
            
            channel = QWebChannel(view.page())
            channel.registerObject("bridge", self.bridge)
            view.page().setWebChannel(channel)
            
            # Verificar que el archivo existe
            tarjetas_path = Path("ui/entrevista_ui/tarjetas.html").resolve()
            if not tarjetas_path.exists():
                QMessageBox.critical(self, "Error", f"No se encontró el archivo: {tarjetas_path}")
                # Crear un HTML básico como fallback
                view.setHtml(f"""
                    <html>
                    <body style='background: #f8fff8; color: black; font-family: Arial; padding: 20px;'>
                        <h2>Prototipo: {self.tab_names[i]}</h2>
                        <p>Archivo tarjetas.html no encontrado en:</p>
                        <code>{tarjetas_path}</code>
                        <p>Esta pestaña mostraría: {carta_id}</p>
                    </body>
                    </html>
                """)
            else:
                print(f"Cargando: {tarjetas_path}")
                view.load(QUrl.fromLocalFile(str(tarjetas_path)))
            
            # Conectar señal de carga completada
            view.loadFinished.connect(lambda ok, idx=i: self.on_webview_loaded(ok, idx))
            self.webviews[i] = view
            self.webviews_loaded[i] = False  # Inicializar como no cargado
            self.tabs.addTab(view, self.tab_names[i])

        self.tabs.hide()  # Ocultar al inicio
        tabs_layout.addWidget(self.tabs)

        self.layout.addWidget(self.tabs_container)

    def on_webview_loaded(self, ok, index):
        """Callback cuando un WebView termina de cargar"""
        if ok:
            self.webviews_loaded[index] = True
            print(f"WebView {index} cargado correctamente")
        else:
            print(f"Error cargando WebView {index}")

    def crear_footer(self):
        """Crear pie de página con información"""
        footer_frame = QFrame()
        footer_frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                border: 2px solid {COLOR_PALETTE['PALE_GREEN']};
                padding: 15px;
            }}
        """)
        footer_layout = QHBoxLayout(footer_frame)

        # Cronómetro
        timer_frame = QFrame()
        timer_frame.setStyleSheet("""
            QFrame {
                background: rgba(232, 245, 233, 0.8);
                border-radius: 10px;
                border: 1px solid #a5d6a7;
                padding: 10px;
            }
        """)
        timer_layout = QHBoxLayout(timer_frame)
        
        timer_icon = QLabel("⏱️")
        timer_icon.setFont(QFont("Segoe UI", 14))
        timer_layout.addWidget(timer_icon)
        
        self.cronometro = QLabel("00:00")
        self.cronometro.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.cronometro.setStyleSheet("color: #1b5e20;")
        timer_layout.addWidget(self.cronometro)
        
        footer_layout.addWidget(timer_frame)

        # Información de estado
        self.lbl_estado = QLabel("🟢 Entrevista en curso")
        self.lbl_estado.setFont(QFont("Segoe UI", 12))
        self.lbl_estado.setStyleSheet("color: #2e7d32; background: rgba(200, 230, 201, 0.7); padding: 8px 15px; border-radius: 8px;")
        footer_layout.addWidget(self.lbl_estado)

        footer_layout.addStretch()

        self.layout.addWidget(footer_frame)

        # Inicializar timer
        self.tiempo_inicio = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_cronometro)
        self.timer.start(1000)

    def actualizar_pregunta(self):
        """Actualiza el texto de la pregunta y muestra/oculta tabs según categoría"""
        cat = self.categorias[self.categoria_idx]
        preguntas_cat = self.preguntas.obtener_preguntas(cat)
        
        # Actualizar barra de progreso
        total_preguntas = sum(len(self.preguntas.obtener_preguntas(c)) for c in self.categorias)
        preguntas_completadas = sum(len(self.preguntas.obtener_preguntas(self.categorias[i])) 
                                  for i in range(self.categoria_idx)) + self.pregunta_idx
        progreso = int((preguntas_completadas / total_preguntas) * 100) if total_preguntas > 0 else 0
        
        self.progress_bar.setValue(progreso)
        self.lbl_progreso.setText(f"{preguntas_completadas}/{total_preguntas} preguntas")

        if self.pregunta_idx < len(preguntas_cat):
            # Actualizar categoría
            self.lbl_categoria.setText(f"📁 Categoría: {cat}")
            
            # Actualizar pregunta
            pregunta_texto = preguntas_cat[self.pregunta_idx]['texto']
            self.lbl_pregunta.setText(pregunta_texto)
            print(f"Mostrando pregunta: {cat} - Índice: {self.pregunta_idx}")
        else:
            self.lbl_pregunta.setText("✅ ¡Entrevista finalizada!")
            self.lbl_categoria.setText("🎉 Completado")
            self.lbl_estado.setText("✅ Entrevista finalizada")
            self.tabs.hide()
            self.tabs_title.hide()
            return

        # Mostrar tabs solo para categorías visuales
        if cat in self.VISUAL_CATEGORIES:
            self.tabs.show()
            self.tabs_title.show()
            # Mostrar la carta correspondiente con un pequeño delay
            idx = self.VISUAL_CATEGORIES.index(cat)
            self.tabs.setCurrentIndex(idx)
            print(f"Mostrando tab visual: {self.tab_names[idx]} para categoría: {cat}")
            
            # Esperar a que el WebView esté cargado antes de mostrar la carta
            if self.webviews_loaded.get(idx, False):
                self.mostrar_carta(idx, self.carta_ids[idx])
            else:
                # Si no está cargado, intentar después de un delay
                QTimer.singleShot(1000, lambda: self.mostrar_carta(idx, self.carta_ids[idx]))
        else:
            self.tabs.hide()
            self.tabs_title.hide()
            print(f"Ocultando tabs - Categoría no visual: {cat}")

    def actualizar_desde_bridge(self, categoria, pregunta_idx):
        """Actualiza la pregunta y tabs según la señal del entrevistador"""
        print(f"Actualizando desde bridge: {categoria}, índice: {pregunta_idx}")
        if categoria in self.categorias:
            self.categoria_idx = self.categorias.index(categoria)
            self.pregunta_idx = pregunta_idx
            self.actualizar_pregunta()

    def siguiente_pregunta(self):
        """Avanza a la siguiente pregunta y actualiza la vista"""
        self.pregunta_idx += 1
        cat = self.categorias[self.categoria_idx]
        preguntas_cat = self.preguntas.obtener_preguntas(cat)
        
        if self.pregunta_idx >= len(preguntas_cat):
            self.categoria_idx += 1
            self.pregunta_idx = 0
            if self.categoria_idx >= len(self.categorias):
                self.lbl_pregunta.setText("✅ ¡Entrevista finalizada!")
                self.lbl_categoria.setText("🎉 Completado")
                self.lbl_estado.setText("✅ Entrevista finalizada")
                self.tabs.hide()
                self.tabs_title.hide()
                return
                
        self.actualizar_pregunta()

    @Slot(dict)
    def on_update_data(self, data):
        """Actualizar las vistas HTML con los datos del entrevistador"""
        print(f"Actualizando datos en WebViews: {data}")
        for i, view in self.webviews.items():
            if self.webviews_loaded.get(i, False):
                js_code = f"actualizarTodo({data['humedad']}, {data['temperatura']}, {data['lluvia']}, {data['viento']})"
                view.page().runJavaScript(js_code)
                print(f"Ejecutando JS en view {i}: {js_code}")

    def mostrar_carta(self, tab_index, carta_id):
        """Ejecuta la función JS mostrarCarta en la tab correspondiente"""
        if tab_index in self.webviews and self.webviews_loaded.get(tab_index, False):
            js_code = f"mostrarCarta('{carta_id}')"
            self.webviews[tab_index].page().runJavaScript(js_code)
            print(f"Mostrando carta: {carta_id} en tab {tab_index}")
        else:
            print(f"WebView {tab_index} no está listo para mostrar carta {carta_id}")

    def actualizar_cronometro(self):
        """Actualizar el cronómetro"""
        self.tiempo_inicio += 1
        minutos = self.tiempo_inicio // 60
        segundos = self.tiempo_inicio % 60
        self.cronometro.setText(f"{minutos:02d}:{segundos:02d}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Configurar paleta de colores global
    app.setStyle('Fusion')
    
    bridge = DataBridge()
    win = IntervieweeScreen(bridge)
    win.show()
    sys.exit(app.exec())