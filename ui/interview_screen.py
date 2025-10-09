import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QTabWidget, QMessageBox, QInputDialog
)
from PySide6.QtCore import QTimer, QObject, Signal, Slot, QUrl
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
import cv2
from pathlib import Path
import time
from datetime import datetime

from ui.interviewee_screen import IntervieweeScreen

from classes.entrevista import Entrevista
from classes.entrevista_preguntas import EntrevistaPreguntas
from classes.marca import Marca
from classes.marcas import Marcas
from video_io.video import obtener_capturador, CapturadorVideo


# ---- Bridge Python ↔ JS ----
class DataBridge(QObject):
    updateData = Signal(dict)  # ya existente
    updatePregunta = Signal(str, int)  # categoría, índice de pregunta

    @Slot(int, int, int, int)
    def setValues(self, humedad, temperatura, lluvia, viento):
        self.updateData.emit({
            "humedad": humedad,
            "temperatura": temperatura,
            "lluvia": lluvia,
            "viento": viento
        })

    @Slot()
    def ping(self):
        """Slot de diagnóstico: invocarlo desde JS para comprobar conectividad."""
        print("[DEBUG] DataBridge.ping() recibido desde JS")

    @Slot(dict)
    def on_update_data(self, data):
        """Reenviar los datos recibidos desde controls.html al entrevistado"""
        if hasattr(self, "entrevistado_window"):
            self.entrevistado_window.on_update_data(data)
            
    @Slot(str, int)
    def setPregunta(self, categoria, pregunta_idx):
        """Señal para actualizar la pregunta del entrevistado"""
        self.updatePregunta.emit(categoria, pregunta_idx)


class InterviewScreen(QWidget):
    def __init__(self, entrevista_id=None):
        super().__init__()
        self.setWindowTitle("Entrevista UX - Campesinas")
        self.resize(1400, 800)

        
        # Core logic
        self.entrevista = None
        self.preguntas = EntrevistaPreguntas()
        self.categorias = list(self.preguntas.preguntas.keys())
        self.categoria_idx = 0
        self.pregunta_idx = 0
        self.current_pregunta_id = 1  # ID incremental para preguntas

        # Video capturador y marcas (se inicializan por grabación)
        self.capturador = None
        self.is_recording = False
        self.output_file = None
        self.marcas = None
        self.start_time = None  # Para calcular timestamps relativos

        # Estados de la pregunta actual
        self.pregunta_iniciada = False
        self.pregunta_finalizada = False

        # Inicializar bridge y estructura de webviews antes de crear la ventana del entrevistado
        self.bridge = DataBridge()
        self.webviews = {}

        # Crear y mostrar la ventana del entrevistado pasando el mismo bridge
        self.entrevistado_window = IntervieweeScreen(self.bridge)
        self.entrevistado_window.show()
        
        
        layout = QHBoxLayout(self)

        # Cronómetro
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

        # Estilos iniciales para botones de flujo
        self.btn_siguiente.setStyleSheet("background-color: red; color: white;")
        self.btn_siguiente.setEnabled(False)
        self.btn_fin.setEnabled(False)

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

        # Panel de controles (usar self.bridge ya inicializado)
        self.controls_view = QWebEngineView()
        channel_controls = QWebChannel(self.controls_view.page())
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

        layout.addLayout(right_layout, 5)

        # Conectar la señal updateData a un slot para reenviar (bridge ya inicializado)
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
        self.timer.start(33)  # Aproximadamente 30 FPS

        self.actualizar_pregunta()

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

    def actualizar_cronometro(self):
        self.tiempo_inicio += 1
        minutos = self.tiempo_inicio // 60
        segundos = self.tiempo_inicio % 60
        self.lbl_cronometro.setText(f"{minutos:02d}:{segundos:02d}")
    
    def on_update_data(self, data):
        """Reenviar los datos recibidos desde controls.html al entrevistado"""
        if hasattr(self, "entrevistado_window") and self.entrevistado_window:
            self.entrevistado_window.on_update_data(data)
        
    def toggle_grabacion(self):
        if not self.is_recording:
            try:
                # === Generar nombre de entrevista y pedir ID ===
                videos_path = Path("data/videos_originales")
                max_num = 0
                today = datetime.now().strftime('%Y-%m-%d')
                if videos_path.exists():
                    for video in videos_path.glob("interview_*.mp4"):
                        try:
                            video_id = video.stem.split("interview_")[1]
                            date_part, num_part = video_id.split("_")
                            if date_part == today:
                                num = int(num_part)
                                max_num = max(max_num, num)
                        except (IndexError, ValueError):
                            continue
                next_num = max_num + 1
                default_id = f"{today}_{next_num:03d}"
                nombre_archivo = f"interview_{default_id}.mp4"
                input_dialog = QInputDialog(self)
                input_dialog.setWindowTitle("ID de Entrevista")
                input_dialog.setLabelText("Ingrese el ID de la entrevista:")
                input_dialog.setTextValue(nombre_archivo)
                input_dialog.setStyleSheet("""
                    QInputDialog { color: black; background-color: white; }
                    QLabel { color: black; background-color: white; }
                    QLineEdit { color: black; background-color: white; border: 1px solid gray; }
                    QPushButton { color: black; background-color: lightgray; border: 1px solid gray; padding: 5px 10px; }
                    QPushButton:hover { background-color: gray; color: white; }
                """)
                ok = input_dialog.exec_()
                entrevista_id = input_dialog.textValue().strip()
                if not ok:
                    QMessageBox.information(self, "Cancelado", "La grabación fue cancelada por el usuario.")
                    return
                try:
                    prefix, date_part, num_part_ext = entrevista_id.split("_", 2)
                    num_part = num_part_ext.split(".")[0]
                    if prefix != "interview" or date_part != today or not num_part.isdigit():
                        raise ValueError
                except ValueError:
                    QMessageBox.critical(self, "Error", "El nombre debe tener formato: interview_YYYY-MM-DD_NNN.mp4")
                    return
                # === Nueva instancia de Entrevista y Marcas ===
                self.id = f"{date_part}_{num_part}"
                self.output_file = videos_path / entrevista_id
                self.output_file.parent.mkdir(parents=True, exist_ok=True)
                self.entrevista = Entrevista(entrevista_id=self.id)
                self.capturador = self.entrevista.capturador
                self.marcas = self.entrevista.marcas
                self.current_pregunta_id = 1
                self.categoria_idx = 0
                self.pregunta_idx = 0
                # Reset estados de pregunta al iniciar grabación
                self.pregunta_iniciada = False
                self.pregunta_finalizada = False
                self.btn_inicio.setStyleSheet("")
                self.btn_inicio.setEnabled(True)
                self.btn_fin.setStyleSheet("")
                self.btn_fin.setEnabled(False)
                self.btn_siguiente.setStyleSheet("background-color: red; color: white;")
                self.btn_siguiente.setEnabled(False)
                # Iniciar grabación
                self.tiempo_inicio = 0
                self.lbl_cronometro.setText("00:00")
                self.capturador.iniciar_grabacion(str(self.output_file), resolucion="720p", audio="AAC")
                self.is_recording = True
                self.start_time = time.time()
                self.cronometro_timer.start(1000)
                self.btn_grabar.setText("⏹️ Detener Grabación")
                print(f"Grabación iniciada: {self.output_file}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo iniciar la grabación: {str(e)}")
        else:
            try:
                self.capturador.detener_grabacion()
                self.is_recording = False
                self.start_time = None
                self.cronometro_timer.stop()
                self.btn_grabar.setText("🎥 Iniciar Grabación")
                # Guardar marcas y exportar json al finalizar
                if self.marcas:
                    self.marcas.exportar_json(self.entrevista.marcas_json)
                print("Grabación detenida")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo detener la grabación: {str(e)}")

    def marcar_inicio(self):
        if not self.is_recording:
            QMessageBox.warning(self, "Advertencia", "Debe iniciar la grabación primero")
            return
        try:
            timestamp = time.time() - self.start_time
            nota = self.txt_comentarios.toPlainText().strip()

            marca = Marca(
                entrevista_id=self.entrevista.id,
                pregunta_id=self.current_pregunta_id,
                inicio=timestamp,
                fin=None,
                nota=nota
            )

            # Agregar la marca sin guardar aún en archivo
            self.marcas.marcas.append(marca)
            print(f"Marca de inicio creada para pregunta {self.current_pregunta_id} en {timestamp:.2f}s")

            self.btn_inicio.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
            self.btn_inicio.setEnabled(False)
            self.pregunta_iniciada = True

            self.btn_fin.setEnabled(True)
            self.btn_fin.setStyleSheet("background-color: orange; color: white; font-weight: bold;")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo crear la marca: {str(e)}")


    def marcar_fin(self):
        if not self.is_recording:
            QMessageBox.warning(self, "Advertencia", "Debe iniciar la grabación primero")
            return
        if not self.pregunta_iniciada:
            QMessageBox.warning(self, "Advertencia", "Debe marcar el inicio de la pregunta primero")
            return

        try:
            timestamp = time.time() - self.start_time
            marca = self.marcas.buscar_marcas_por_pregunta_id(self.current_pregunta_id)
            if marca:
                marca.fin = timestamp
                marca.nota = self.txt_comentarios.toPlainText().strip()
                print(f"Marca de fin actualizada para pregunta {self.current_pregunta_id} en {timestamp:.2f}s")

                # Ahora sí guardar todo el conjunto de marcas actualizado
                self.marcas._guardar_marcas_json()

                self.pregunta_finalizada = True
                self.btn_fin.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
                self.btn_fin.setEnabled(False)
                self.btn_siguiente.setStyleSheet("background-color: orange; color: white; font-weight: bold;")
                self.btn_siguiente.setEnabled(True)
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
        if not self.pregunta_finalizada:
            QMessageBox.warning(self, "Advertencia", "Debe marcar el fin de la pregunta primero")
            return
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
        print("se prepara el envio")
        self.bridge.setPregunta(cat, self.pregunta_idx)
        print("se envio")
        # Reset estados y estilos para la nueva pregunta
        self.pregunta_iniciada = False
        self.pregunta_finalizada = False
        self.btn_inicio.setStyleSheet("")
        self.btn_inicio.setEnabled(True)
        self.btn_fin.setStyleSheet("")
        self.btn_fin.setEnabled(False)
        self.btn_siguiente.setStyleSheet("background-color: red; color: white;")
        self.btn_siguiente.setEnabled(False)

    def closeEvent(self, event):
        if self.is_recording and self.capturador:
            self.capturador.detener_grabacion()
            if self.marcas:
                self.marcas._guardar_marcas_json()
        if self.cap:
            self.cap.release()
        event.accept()

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def show_error(self, msg):
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Error")
        msgbox.setText(msg)
        msgbox.setIcon(QMessageBox.Critical)
        msgbox.setStyleSheet("""
            QLabel { 
                color: black; 
                background-color: white; 
            }
        """)
        msgbox.exec()
        self.logger.error(msg)

    def show_warning(self, msg):
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Advertencia")
        msgbox.setText(msg)
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setStyleSheet("""
            QLabel { 
                color: black; 
                background-color: white; 
            }
        """)
        msgbox.exec()
        self.logger.warning(msg)
        
    def show_critical(self, msg):
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Crítico")
        msgbox.setText(msg)
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setStyleSheet("""
            QLabel { 
                color: black; 
                background-color: white; 
            }
        """)
        msgbox.exec()
        self.logger.warning(msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = InterviewScreen()
    win.show()
    sys.exit(app.exec())