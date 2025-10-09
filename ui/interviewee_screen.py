import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTabWidget, QMessageBox,
    QHBoxLayout, QFrame, QProgressBar, QScrollArea
)
from PySide6.QtCore import QTimer, QObject, Signal, Slot, QUrl, Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtGui import QFont
from pathlib import Path

from functools import partial
import unicodedata

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
    
    def __init__(self):
        super().__init__()
        self._current_values = {
            "humedad": 75,
            "temperatura": 28, 
            "lluvia": 15,
            "viento": 12
        }

    @Slot(int, int, int, int)
    def setValues(self, humedad, temperatura, lluvia, viento):
        print(f"🔧 Bridge recibió valores: H={humedad}, T={temperatura}, L={lluvia}, V={viento}")
        self._current_values = {
            "humedad": humedad,
            "temperatura": temperatura,
            "lluvia": lluvia,
            "viento": viento
        }
        self.updateData.emit(self._current_values)

    @Slot()
    def ping(self):
        print("[DEBUG] Interviewee DataBridge.ping() recibido desde JS")

    @Slot(str, int)
    def setPregunta(self, categoria, pregunta_idx):
        """Slot que puede ser llamado desde JS o desde otro bridge para propagar la pregunta."""
        print(f"🔧 Bridge recibió pregunta: {categoria}, índice: {pregunta_idx}")
        self.updatePregunta.emit(categoria, pregunta_idx)
    
    def get_current_values(self):
        """Obtener los valores actuales"""
        return self._current_values


class IntervieweeScreen(QWidget):
    VISUAL_CATEGORIES = ["Semaforo", "Pictogramas", "Tabla"]

    def _normalize(self, s: str) -> str:
        """Normaliza strings: quita acentos y pasa a minúsculas."""
        if not isinstance(s, str):
            return ""
        s_norm = unicodedata.normalize('NFKD', s)
        s_norm = ''.join(ch for ch in s_norm if not unicodedata.combining(ch))
        return s_norm.lower()

    def __init__(self, bridge: DataBridge):
        super().__init__()
        self.setWindowTitle("🌱 Entrevista UX - Pantalla Entrevistado")
        self.resize(1600, 1000)
        
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
        self.webviews_loaded = {}
        self.web_channels = {}
        self.current_carta_id = None
        
        self.tiempo_inicio = 0
        self.total_preguntas = sum(len(self.preguntas.obtener_preguntas(c)) for c in self.categorias)
        self.preguntas_completadas = 0

        # Hacer la ventana scrollable: crear un QScrollArea y un widget contenedor
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll.setWidget(self.scroll_widget)

        # Layout principal del contenido (usar self.layout por compatibilidad con el resto del código)
        self.layout = QVBoxLayout(self.scroll_widget)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(25, 25, 25, 25)

        # Añadir el scroll area al layout principal de la ventana
        main_layout.addWidget(self.scroll)

        # Conectar señales
        self.bridge.updateData.connect(self.on_update_data)
        self.bridge.updatePregunta.connect(self.actualizar_desde_bridge)

        self.crear_header()
        self.crear_area_pregunta()
        self.crear_tabs_visuales()
        self.crear_footer()

        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_cronometro)
        self.timer.start(1000)

        # Mostrar la primera pregunta inmediatamente
        self.actualizar_pregunta()

    def crear_tabs_visuales(self):
        """Crear tabs para los prototipos visuales - VERSIÓN SIMPLIFICADA"""
        self.tabs_container = QFrame()
        self.tabs_container.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
            }
        """)
        tabs_layout = QVBoxLayout(self.tabs_container)
        tabs_layout.setSpacing(8)
        tabs_layout.setContentsMargins(0, 0, 0, 0)

        self.tabs_title = QLabel("📊 Prototipos Visuales")
        self.tabs_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.tabs_title.setStyleSheet("color: white; padding: 8px;")
        self.tabs_title.setAlignment(Qt.AlignCenter)
        tabs_layout.addWidget(self.tabs_title)

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
                padding: 10px 18px;
                margin-right: 2px;
                color: black;
                font-weight: bold;
                font-size: 13px;
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
            view.setMinimumHeight(500)
            
            # Configuración básica del WebChannel
            channel = QWebChannel()
            channel.registerObject("bridge", self.bridge)
            view.page().setWebChannel(channel)
            self.web_channels[i] = channel

            # Cargar el archivo HTML
            tarjetas_path = Path("ui/entrevista_ui/tarjetas.html").resolve()
            if tarjetas_path.exists():
                print(f"📁 Cargando archivo: {tarjetas_path}")
                view.load(QUrl.fromLocalFile(str(tarjetas_path)))
            else:
                # HTML de fallback simple
                fallback_html = f"""
                <html><body style='background: #f8fff8; padding: 20px;'>
                    <h2>{self.tab_names[i]}</h2>
                    <p>Cargando interfaz...</p>
                </body></html>
                """
                view.setHtml(fallback_html)
                print(f"⚠️  Usando HTML de fallback para tab {i}")
            
            # Conectar señal de carga completada
            view.loadFinished.connect(partial(self.on_webview_loaded, index=i, carta_id=carta_id))
            self.webviews[i] = view
            self.webviews_loaded[i] = False
            self.tabs.addTab(view, self.tab_names[i])

        # Ocultar tabs al inicio - se mostrarán según la categoría
        self.tabs.hide()
        self.tabs_title.hide()
        tabs_layout.addWidget(self.tabs)
        self.layout.addWidget(self.tabs_container, stretch=1)

    def on_webview_loaded(self, ok, index, carta_id):
        """Callback cuando un WebView termina de cargar"""
        if ok:
            self.webviews_loaded[index] = True
            print(f"✅ WebView {index} cargado correctamente")
            
            # Forzar que esta webview muestre su carta correspondiente después de un pequeño delay
            QTimer.singleShot(500, lambda idx=index, cid=carta_id: self.mostrar_carta_simple(idx, cid))

            # Enviar datos actuales si están disponibles (un poco después)
            QTimer.singleShot(1000, lambda idx=index: self.enviar_datos_simple(idx))
        else:
            print(f"❌ Error cargando WebView {index}")

    def mostrar_carta_simple(self, tab_index, carta_id):
        """Mostrar carta de manera simple"""
        if tab_index in self.webviews and self.webviews_loaded.get(tab_index, False):
            js_code = f"mostrarCarta('{carta_id}')"
            self.webviews[tab_index].page().runJavaScript(js_code)
            print(f"📋 Mostrando carta: {carta_id} en tab {tab_index}")

    def enviar_datos_simple(self, tab_index):
        """Enviar datos actuales a un WebView"""
        if tab_index in self.webviews and self.webviews_loaded.get(tab_index, False):
            try:
                # Usar los valores actuales del bridge
                current_values = self.bridge._current_values
                js_code = f"""
                    if (typeof actualizarTodo === 'function') {{
                        actualizarTodo({current_values['humedad']}, {current_values['temperatura']}, {current_values['lluvia']}, {current_values['viento']});
                    }}
                """
                self.webviews[tab_index].page().runJavaScript(js_code)
                print(f"📊 Datos enviados a tab {tab_index}: {current_values}")
            except Exception as e:
                print(f"❌ Error enviando datos a tab {tab_index}: {e}")

    @Slot(dict)
    def on_update_data(self, data):
        """Actualizar las vistas HTML con los datos del entrevistador"""
        print(f"🔄 Actualizando datos en WebViews: {data}")
        
        for i, view in self.webviews.items():
            if self.webviews_loaded.get(i, False):
                js_code = f"actualizarTodo({data['humedad']}, {data['temperatura']}, {data['lluvia']}, {data['viento']})"
                view.page().runJavaScript(js_code)
                print(f"🔄 Ejecutando JS en view {i}: {js_code}")

    def actualizar_pregunta(self):
        """Actualiza el texto de la pregunta y muestra/oculta tabs según categoría"""
        cat = self.categorias[self.categoria_idx]
        # Normalizar categoría para comparaciones (minusculas y sin acentos)
        visual_norms = [self._normalize(v) for v in self.VISUAL_CATEGORIES]
        cat_norm = self._normalize(cat)
        preguntas_cat = self.preguntas.obtener_preguntas(cat)
        
        # Calcular progreso
        self.preguntas_completadas = sum(
            len(self.preguntas.obtener_preguntas(self.categorias[i])) 
            for i in range(self.categoria_idx)
        ) + self.pregunta_idx
        
        progreso = int((self.preguntas_completadas / self.total_preguntas) * 100) if self.total_preguntas > 0 else 0
        
        self.progress_bar.setValue(progreso)
        self.lbl_progreso.setText(f"{self.preguntas_completadas}/{self.total_preguntas} preguntas")

        if self.pregunta_idx < len(preguntas_cat):
            self.lbl_categoria.setText(f"📁 Categoría: {cat}")
            pregunta_texto = preguntas_cat[self.pregunta_idx]['texto']
            self.lbl_pregunta.setText(pregunta_texto)
            print(f"📝 Mostrando pregunta: {cat} - Índice: {self.pregunta_idx}")
        else:
            self.lbl_pregunta.setText("✅ ¡Entrevista finalizada!")
            self.lbl_categoria.setText("🎉 Completado")
            self.lbl_estado.setText("✅ Entrevista finalizada")
            self.tabs.hide()
            self.tabs_title.hide()
            return

        # Mostrar tabs solo para categorías visuales - CORREGIDO
        if cat_norm in visual_norms:
            self.tabs.show()
            self.tabs_title.show()
            idx = visual_norms.index(cat_norm)
            self.tabs.setCurrentIndex(idx)
            self.current_carta_id = self.carta_ids[idx]

            print(f"🎨 Mostrando tab visual: {self.tab_names[idx]} para categoría: {cat}")

            # Mostrar la carta correspondiente
            if self.webviews_loaded.get(idx, False):
                self.mostrar_carta_simple(idx, self.carta_ids[idx])
            else:
                print(f"⏳ WebView {idx} no está listo, reintentando...")
                QTimer.singleShot(1000, lambda: self.mostrar_carta_simple(idx, self.carta_ids[idx]))

        else:
            self.tabs.hide()
            self.tabs_title.hide()
            self.current_carta_id = None
            print(f"🔍 Ocultando tabs - Categoría no visual: {cat}")

    def actualizar_desde_bridge(self, categoria, pregunta_idx):
        """Actualiza la pregunta y tabs según la señal del entrevistador"""
        print(f"🔄 Actualizando desde bridge: {categoria}, índice: {pregunta_idx}")
        # Buscar la categoría de forma normalizada
        cat_norm = self._normalize(categoria)
        for i, c in enumerate(self.categorias):
            if self._normalize(c) == cat_norm:
                self.categoria_idx = i
                self.pregunta_idx = pregunta_idx
                self.actualizar_pregunta()
                return
        print(f"[WARN] Categoria recibida desde bridge no encontrada tras normalizar: {categoria}")

    def crear_header(self):
        """Crear encabezado con diseño agrícola"""
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(46, 125, 50, 0.9),
                    stop:0.5 rgba(56, 142, 60, 0.85),
                    stop:1 rgba(76, 175, 80, 0.8));
                border-radius: 20px;
                border: 3px solid rgba(255, 255, 255, 0.3);
                padding: 15px;
            }}
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(10)

        # Título principal
        title = QLabel("🎯 Pantalla del Entrevistado")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: white;
                background: transparent;
                padding: 8px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
        """)
        header_layout.addWidget(title)

        # Subtítulo
        subtitle = QLabel("Interfaz para visualización de prototipos durante la entrevista UX")
        subtitle.setFont(QFont("Segoe UI", 13))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: #e8f5e9;
                background: rgba(255, 255, 255, 0.1);
                padding: 6px 15px;
                border-radius: 12px;
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
                border-radius: 18px;
                border: 3px solid {COLOR_PALETTE['LIGHT_GREEN']};
                padding: 20px;
            }}
        """)
        pregunta_frame.setMaximumHeight(220)
        pregunta_layout = QVBoxLayout(pregunta_frame)
        pregunta_layout.setSpacing(8)

        # Etiqueta de categoría
        self.lbl_categoria = QLabel()
        self.lbl_categoria.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.lbl_categoria.setStyleSheet("""
            QLabel {
                color: #1b5e20;
                background: rgba(232, 245, 233, 0.8);
                padding: 6px 12px;
                border-radius: 8px;
                border: 1px solid #a5d6a7;
            }
        """)
        pregunta_layout.addWidget(self.lbl_categoria)

        # Pregunta actual
        self.lbl_pregunta = QLabel()
        self.lbl_pregunta.setWordWrap(True)
        self.lbl_pregunta.setFont(QFont("Segoe UI", 16))
        self.lbl_pregunta.setStyleSheet("""
            QLabel {
                color: black;
                background: rgba(248, 255, 248, 0.9);
                padding: 15px;
                border-radius: 12px;
                border: 2px solid #c8e6c9;
                line-height: 1.3;
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
                border-radius: 8px;
                text-align: center;
                background: #f1f8e9;
                height: 18px;
                color: black;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4caf50, stop:1 #2e7d32);
                border-radius: 6px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.lbl_progreso = QLabel()
        self.lbl_progreso.setFont(QFont("Segoe UI", 10))
        self.lbl_progreso.setStyleSheet("color: #555; padding: 3px;")
        progress_layout.addWidget(self.lbl_progreso)
        
        pregunta_layout.addWidget(self.progress_frame)

        self.layout.addWidget(pregunta_frame)

    def crear_footer(self):
        """Crear pie de página con información"""
        footer_frame = QFrame()
        footer_frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(255, 255, 255, 0.9);
                border-radius: 12px;
                border: 2px solid {COLOR_PALETTE['PALE_GREEN']};
                padding: 10px;
            }}
        """)
        footer_frame.setMaximumHeight(60)
        footer_layout = QHBoxLayout(footer_frame)

        # Cronómetro
        timer_frame = QFrame()
        timer_frame.setStyleSheet("""
            QFrame {
                background: rgba(232, 245, 233, 0.8);
                border-radius: 8px;
                border: 1px solid #a5d6a7;
                padding: 8px;
            }
        """)
        timer_layout = QHBoxLayout(timer_frame)
        
        timer_icon = QLabel("⏱️")
        timer_icon.setFont(QFont("Segoe UI", 13))
        timer_layout.addWidget(timer_icon)
        
        self.cronometro = QLabel("00:00")
        self.cronometro.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        self.cronometro.setStyleSheet("color: #1b5e20;")
        timer_layout.addWidget(self.cronometro)
        
        footer_layout.addWidget(timer_frame)

        # Información de estado
        self.lbl_estado = QLabel("🟢 Entrevista en curso")
        self.lbl_estado.setFont(QFont("Segoe UI", 11))
        self.lbl_estado.setStyleSheet("color: #2e7d32; background: rgba(200, 230, 201, 0.7); padding: 6px 12px; border-radius: 6px;")
        footer_layout.addWidget(self.lbl_estado)

        footer_layout.addStretch()

        self.layout.addWidget(footer_frame)

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

    def actualizar_cronometro(self):
        """Actualizar el cronómetro (continúa sin reiniciarse)"""
        self.tiempo_inicio += 1
        minutos = self.tiempo_inicio // 60
        segundos = self.tiempo_inicio % 60
        self.cronometro.setText(f"{minutos:02d}:{segundos:02d}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    bridge = DataBridge()
    win = IntervieweeScreen(bridge)
    win.show()
    sys.exit(app.exec())