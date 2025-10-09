from tensorflow.keras.models import load_model
import cv2
import numpy as np
import logging
from pathlib import Path
from collections import defaultdict
import mediapipe as mp



class Analisis:
    def __init__(self, modelo_path):
        self.logger = logging.getLogger(__name__)
        self.modelo_path = Path(modelo_path)

        # Mapear índices a emociones
        self.emotion_map = {
            0: "angry",
            1: "contempt",
            2: "disgust",
            3: "fear",
            4: "happy",
            5: "sad",
            6: "surprise"
        }

        if not self.modelo_path.exists():
            self.logger.error(f"El modelo no se encontró en la ruta: {self.modelo_path}")
            raise FileNotFoundError(f"No se encontró el modelo en la ruta: {self.modelo_path}")

        try:
            self.model = load_model(self.modelo_path)
            self.logger.info("Modelo cargado exitosamente.")
        except Exception as e:
            self.logger.error(f"Error al cargar el modelo: {e}")
            raise RuntimeError(f"No se pudo cargar el modelo: {e}")

        # Inicializar MediaPipe para detección de rostro
        self.mp_face = mp.solutions.face_detection
        self.face_detection = self.mp_face.FaceDetection(
            model_selection=1, min_detection_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils  # Opcional, si quieres dibujar bounds

    def __del__(self):
        """Cierra MediaPipe al destruir la instancia."""
        if hasattr(self, 'face_detection'):
            self.face_detection.close()

    def preprocess_frame(self, frame, target_size=(224, 224)):
        """Preprocesa un frame para el modelo (BGR → RGB + resize + normalización)."""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = cv2.resize(frame_rgb, target_size)
        img = img.astype("float32") / 255.0
        img = np.expand_dims(img, axis=0)
        return img

    def crop_face(self, frame, padding=0.2):
        """Recorta el rostro usando MediaPipe. Devuelve None si no se detecta rostro.
        padding: Agrega % extra alrededor del bbox para contexto.
        """
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_detection.process(rgb_frame)
            if not results.detections:
                return None
            
            bbox = results.detections[0].location_data.relative_bounding_box  # Primera cara
            h, w, _ = frame.shape
            
            # Calcular bounds con padding
            x1 = max(int(bbox.xmin * w - padding * w), 0)
            y1 = max(int(bbox.ymin * h - padding * h), 0)
            x2 = min(int((bbox.xmin + bbox.width) * w + padding * w), w)
            y2 = min(int((bbox.ymin + bbox.height) * h + padding * h), h)
            
            cropped = frame[y1:y2, x1:x2]
            # Si cropped es muy pequeño (<50x50), ignora
            if cropped.shape[0] < 50 or cropped.shape[1] < 50:
                return None
            
            return cropped
        except Exception as e:
            self.logger.warning(f"Error en crop_face: {e}")
            return None

    def analizar_fragmento(self, fragmento_path, skip_frames=1):
        """Analiza un fragmento de video y devuelve la intensidad de cada emoción por frame."""
        fragmento_path = Path(fragmento_path)
        if not fragmento_path.exists():
            self.logger.error(f"El fragmento no se encontró en la ruta: {fragmento_path}")
            raise FileNotFoundError(f"No se encontró el fragmento en la ruta: {fragmento_path}")

        cap = cv2.VideoCapture(str(fragmento_path))
        resultados = []
        frame_count = 0

        if not cap.isOpened():
            self.logger.error(f"No se pudo abrir el video: {fragmento_path}")
            raise RuntimeError(f"No se pudo abrir el video: {fragmento_path}")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_count += 1
                if frame_count % skip_frames != 0:
                    continue

                # Recortar rostro
                cropped = self.crop_face(frame)
                if cropped is None:
                    continue  # No se detectó rostro

                # Preprocesar y predecir
                processed = self.preprocess_frame(cropped)
                prediction = self.model.predict(processed, verbose=0)[0]
                intensidades = {self.emotion_map[i]: float(prediction[i]) for i in range(len(prediction))}
                resultados.append(intensidades)
        finally:
            cap.release()

        self.logger.info(f"Procesados {len(resultados)} frames de {frame_count} totales.")
        return resultados

    def get_emotion_summary(self, resultados):
        """Resumen simple: promedio de intensidades y emoción dominante."""
        if not resultados:
            return {'error': 'No hay resultados para resumir'}
        
        avg_emotions = defaultdict(float)
        for frame_data in resultados:
            for emotion, intensity in frame_data.items():
                avg_emotions[emotion] += intensity / len(resultados)
        
        dominant = max(avg_emotions.items(), key=lambda x: x[1])
        return {
            'dominant_emotion': dominant[0],
            'confidence': dominant[1],
            'avg_intensities': dict(avg_emotions)
        }