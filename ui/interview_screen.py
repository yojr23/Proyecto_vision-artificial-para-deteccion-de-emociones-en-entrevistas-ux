import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QTabWidget, QMessageBox
)
from PySide6.QtCore import QTimer, QObject, Signal, Slot, QUrl
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
import cv2
from pathlib import Path
import time
from datetime import datetime

from classes.entrevista import Entrevista
from classes.entrevista_preguntas import EntrevistaPreguntas
from classes.marca import Marca
from classes.marcas import Marcas
from video_io.video import obtener_capturador, CapturadorVideo


# ---- Bridge Python ↔ JS ----
class DataBridge(QObject):
    updateData = Signal(dict)  # Señal que envía datos al JS

    @Slot(int, int, int, int)
    def setValues(self, humedad, temperatura, lluvia, viento):
        """Señal desde Python para actualizar la interfaz JS"""
        print(f"Enviando valores desde Python: humedad={humedad}, temperatura={temperatura}, lluvia={lluvia}, viento={viento}")
        self.updateData.emit({
            "humedad": humedad,
            "temperatura": temperatura,
            "lluvia": lluvia,
            "viento": viento
        })


class InterviewScreen(QWidget):
    def __init__(self, entrevista_id=None):
        super().__init__()
        self.setWindowTitle("Entrevista UX - Campesinas")
        self.resize(1400, 800)

        # Core logic
        self.entrevista = Entrevista(entrevista_id=entrevista_id)
        self.preguntas = EntrevistaPreguntas()
        self.categorias = list(self.preguntas.preguntas.keys())
        self.categoria_idx = 0
        self.pregunta_idx = 0
        self.current_pregunta_id = 1  # ID incremental para preguntas

        # Video capturador
        self.capturador = obtener_capturador()
        self.is_recording = False
        self.output_file = Path(f"data/videos_originales/interview_{self.entrevista.id}.mp4")
        self.marcas = Marcas(self.entrevista.id, self.output_file)
        self.start_time = None  # Para calcular timestamps relativos

        layout = QHBoxLayout(self)


        #cronometro 
        
        self.cronometro_timer = QTimer()
        self.cronometro_timer.timeout.connect(self.actualizar_cronometro)
        self.tiempo_inicio = 0  # Segundos transcurridos
        

        # ----- Columna izquierda -----
        left_layout = QVBoxLayout()

        self.lbl_pregunta = QLabel("Pregunta: ")
        self.lbl_pregunta.setWordWrap(True)
        self.lbl_pregunta.setStyleSheet("font-size: 18px; font-weight: bold;")
        left_layout.addWidget(self.lbl_pregunta)

        self.btn_grabar = QPushButton("🎥 Iniciar Grabación")
        self.btn_inicio = QPushButton("▶️ Marcar Inicio Pregunta")
        self.btn_fin = QPushButton("⏹️ Marcar Fin Pregunta")
        self.btn_siguiente = QPushButton("➡️ Siguiente Pregunta")

        left_layout.addWidget(self.btn_grabar)
        left_layout.addWidget(self.btn_inicio)
        left_layout.addWidget(self.btn_fin)
        left_layout.addWidget(self.btn_siguiente)


        self.lbl_cronometro = QLabel("00:00")
        self.lbl_cronometro.setStyleSheet("font-size: 16px; font-weight: bold;")
        left_layout.addWidget(self.lbl_cronometro)

        self.txt_comentarios = QTextEdit()
        self.txt_comentarios.setPlaceholderText("Notas / comentarios...")
        left_layout.addWidget(self.txt_comentarios)

        # Panel de controles
        self.controls_view = QWebEngineView()
        channel_controls = QWebChannel(self.controls_view.page())
        self.bridge = DataBridge()
        channel_controls.registerObject("bridge", self.bridge)
        self.controls_view.page().setWebChannel(channel_controls)
        controls_path = Path("ui/entrevista_ui/controls.html").resolve()
        print(f"Cargando controls.html desde: {controls_path}")
        if not controls_path.exists():
            QMessageBox.critical(self, "Error", f"No se encontró el archivo: {controls_path}")
        self.controls_view.load(QUrl.fromLocalFile(str(controls_path)))
        left_layout.addWidget(self.controls_view)

        layout.addLayout(left_layout, 3)

        # ----- Columna derecha -----
        right_layout = QVBoxLayout()

        self.lbl_video = QLabel("Preview cámara")
        self.lbl_video.setStyleSheet("background: black; color: white;")
        right_layout.addWidget(self.lbl_video, 3)

        # Tab con interfaces HTML
        self.tabs = QTabWidget()
        self.webviews = {}
        self.carta_ids = ["carta-semaforo", "carta-visuales", "carta-tabla"]
        self.tab_names = ["Semáforo", "Elementos Visuales", "Tabla"]

        for i, carta_id in enumerate(self.carta_ids):
            view = QWebEngineView()
            channel = QWebChannel(view.page())
            channel.registerObject("bridge", self.bridge)
            view.page().setWebChannel(channel)
            tarjetas_path = Path("ui/entrevista_ui/tarjetas.html").resolve()
            print(f"Cargando tarjetas.html para pestaña {self.tab_names[i]} desde: {tarjetas_path}")
            if not tarjetas_path.exists():
                QMessageBox.critical(self, "Error", f"No se encontró el archivo: {tarjetas_path}")
            view.load(QUrl.fromLocalFile(str(tarjetas_path)))
            # Ejecutar mostrarCarta al cargar la pestaña
            view.loadFinished.connect(lambda ok, idx=i, cid=carta_id: self.mostrar_carta(idx, cid) if ok else print(f"Error cargando pestaña {self.tab_names[idx]}"))
            self.webviews[i] = view
            self.tabs.addTab(view, self.tab_names[i])

        right_layout.addWidget(self.tabs, 2)
        layout.addLayout(right_layout, 5)

        # Conectar la señal updateData a un slot para reenviar
        self.bridge.updateData.connect(self.on_update_data)

        # Eventos
        self.btn_grabar.clicked.connect(self.toggle_grabacion)
        self.btn_inicio.clicked.connect(self.marcar_inicio)
        self.btn_fin.clicked.connect(self.marcar_fin)
        self.btn_siguiente.clicked.connect(self.siguiente_pregunta)

        # Cámara para preview
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error", "No se pudo abrir la cámara")
            sys.exit(1)

        self.timer = QTimer()
        self.timer.timeout.connect(self.mostrar_frame)
        self.timer.start(30)

        self.actualizar_pregunta()

    @Slot(dict)
    def on_update_data(self, data):
        """Reenviar los datos recibidos desde controls.html a todas las vistas"""
        print("on_update_data recibido en Python:", data)
        
        # Actualizar los controles (sincronización visual)
        self.controls_view.page().runJavaScript("actualizarDisplays();")

        # Actualizar todas las tarjetas
        for view in self.webviews.values():
            view.page().runJavaScript(
                f"actualizarTodo({data['humedad']}, {data['temperatura']}, {data['lluvia']}, {data['viento']})"
            )

    def mostrar_carta(self, tab_index, carta_id):
        """Ejecuta la función JS mostrarCarta en la pestaña correspondiente."""
        print(f"Ejecutando mostrarCarta('{carta_id}') en pestaña {self.tab_names[tab_index]}")
        self.webviews[tab_index].page().runJavaScript(f"mostrarCarta('{carta_id}')")

    def mostrar_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Convertir para preview
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            qimg = QImage(frame_rgb.data, w, h, ch * w, QImage.Format_RGB888)
            pix = QPixmap.fromImage(qimg)
            self.lbl_video.setPixmap(pix.scaled(self.lbl_video.size()))

            # Procesar frame para grabación
            if self.is_recording:
                self.capturador.procesar_frame(frame)

            # Detección de emociones (puedes añadir tu lógica aquí)
            # Ejemplo: landmarks = detect_emotions(frame)

    def actualizar_cronometro(self):
            self.tiempo_inicio += 1
            minutos = self.tiempo_inicio // 60
            segundos = self.tiempo_inicio % 60
            self.lbl_cronometro.setText(f"{minutos:02d}:{segundos:02d}")
            
    def toggle_grabacion(self):
        if not self.is_recording:
            try:
                # Crear directorio de salida
                self.output_file.parent.mkdir(parents=True, exist_ok=True)
                # Iniciar grabación
                self.capturador.iniciar_grabacion(str(self.output_file), resolucion="720p")
                self.is_recording = True
                self.start_time = time.time()
                self.cronometro_timer.start(1000) # Actualizar cada segundo
                self.btn_grabar.setText("⏹️ Detener Grabación")
                print(f"Grabación iniciada: {self.output_file}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo iniciar la grabación: {str(e)}")
        else:
            try:
                self.capturador.detener_grabacion()
                self.is_recording = False
                self.start_time = None
                self.btn_grabar.setText("🎥 Iniciar Grabación")
                self.marcas._guardar_marcas_json()
                print("Grabación detenida")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo detener la grabación: {str(e)}")

    def marcar_inicio(self):
        if not self.is_recording:
            QMessageBox.warning(self, "Advertencia", "Debe iniciar la grabación primero")
            return
        try:
            timestamp = time.time() - self.start_time
            nota = self.txt_comentarios.toPlainText()
            marca = Marca(
                entrevista_id=self.entrevista.id,
                pregunta_id=self.current_pregunta_id,
                inicio=timestamp,
                nota=nota
            )
            self.marcas.agregar_marca(marca)
            print(f"Marca de inicio creada para pregunta {self.current_pregunta_id} en {timestamp:.2f}s")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo crear la marca: {str(e)}")


    def marcar_fin(self):
        if not self.is_recording:
            QMessageBox.warning(self, "Advertencia", "Debe iniciar la grabación primero")
            return
        try:
            timestamp = time.time() - self.start_time
            marca = self.marcas.buscar_marcas_por_pregunta_id(self.current_pregunta_id)
            if marca and marca.fin is None:
                marca.fin = timestamp
                self.marcas._guardar_marcas_json()
                print(f"Marca de fin actualizada para pregunta {self.current_pregunta_id} en {timestamp:.2f}s")
            else:
                QMessageBox.warning(self, "Advertencia", "No se encontró una marca de inicio para esta pregunta")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar la marca: {str(e)}")

    def actualizar_pregunta(self):
        cat = self.categorias[self.categoria_idx]
        preguntas_cat = self.preguntas.obtener_preguntas(cat)
        if self.pregunta_idx < len(preguntas_cat):
            self.lbl_pregunta.setText(f"[{cat}] {preguntas_cat[self.pregunta_idx]}")
        else:
            self.lbl_pregunta.setText("✅ Entrevista finalizada")

    def siguiente_pregunta(self):
        self.pregunta_idx += 1
        self.current_pregunta_id += 1
        cat = self.categorias[self.categoria_idx]
        preguntas_cat = self.preguntas.obtener_preguntas(cat)
        if self.pregunta_idx >= len(preguntas_cat):
            self.categoria_idx += 1
            self.pregunta_idx = 0
            if self.categoria_idx >= len(self.categorias):
                self.categoria_idx = len(self.categorias) - 1
                self.pregunta_idx = len(preguntas_cat)
        self.actualizar_pregunta()

    def closeEvent(self, event):
        if self.is_recording:
            self.capturador.detener_grabacion()
            self.marcas._guardar_marcas_json()
        if self.cap:
            self.cap.release()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = InterviewScreen()
    win.show()
    sys.exit(app.exec())