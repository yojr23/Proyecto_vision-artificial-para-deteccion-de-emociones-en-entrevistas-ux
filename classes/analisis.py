from tensorflow.keras.models import load_model
import cv2
import numpy as np
import logging
from pathlib import Path
from collections import defaultdict
import mediapipe as mp
import traceback



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

        # Atributos internos perezosos
        self._model = None
        self._face_detection = None
        self.mp_face = None

        # Intentar cargar el modelo de forma robusta
        try:
            self._load_model()
            self.logger.info("Modelo cargado exitosamente.")
        except Exception as e:
            self.logger.error(f"Error al cargar el modelo: {e}")
            # Propagar un RuntimeError con información útil
            raise RuntimeError(f"No se pudo cargar el modelo: {e}")

    def _load_model(self):
        """Intentar cargar el modelo con varios métodos (TF primero, luego standalone keras)."""
        # Helper: crear clase InputLayer compat que acepte 'batch_shape'
        def make_inputlayer_compat(base_layers_module):
            Base = getattr(base_layers_module, "InputLayer", None)
            if Base is None:
                return None

            class InputLayerCompat(Base):
                @classmethod
                def from_config(cls, config):
                    # Algunos modelos antiguos usaban 'batch_shape' en lugar de 'batch_input_shape'
                    if 'batch_shape' in config and 'batch_input_shape' not in config:
                        config['batch_input_shape'] = tuple(config.pop('batch_shape'))
                    return super(InputLayerCompat, cls).from_config(config)

            return InputLayerCompat

        # NEW: helper para parchear temporalmente InputLayer.from_config (sin crear custom class)
        def _patch_inputlayer_from_config(layers_module):
            InputLayer = getattr(layers_module, "InputLayer", None)
            if InputLayer is None:
                return None
            original = getattr(InputLayer, "from_config", None)
            if original is None:
                return None

            # Crear wrapper que corrige 'batch_shape' -> 'batch_input_shape'
            def patched_from_config(cls, config):
                if isinstance(config, dict) and 'batch_shape' in config and 'batch_input_shape' not in config:
                    config = dict(config)  # copiar para no mutar original
                    config['batch_input_shape'] = tuple(config.pop('batch_shape'))
                # llamar al original (como método de clase)
                return original.__func__(cls, config) if hasattr(original, "__func__") else original(cls, config)

            # asignar como classmethod
            try:
                setattr(InputLayer, "from_config", classmethod(patched_from_config))
            except Exception:
                # si falla la asignación, devolver None para no interrumpir
                return None
            return original

        def _restore_from_config(layers_module, original):
            InputLayer = getattr(layers_module, "InputLayer", None)
            if InputLayer is None or original is None:
                return
            try:
                setattr(InputLayer, "from_config", original)
            except Exception:
                pass

        # Intento 1: tensorflow.keras (con parche temporal si es necesario)
        try:
            import tensorflow as tf
            self.logger.debug("Intentando cargar modelo con tensorflow.keras (parche temporal InputLayer.from_config)...")
            orig = _patch_inputlayer_from_config(tf.keras.layers)
            try:
                # Intentar cargar (parche aplicado si pudo)
                self._model = tf.keras.models.load_model(str(self.modelo_path), compile=False)
            finally:
                # Restaurar siempre el método original
                _restore_from_config(tf.keras.layers, orig)
            return
        except Exception as e_tf:
            self.logger.warning(f"tensorflow.keras.models.load_model falló: {e_tf}")

        # Intento 2: fallback a standalone 'keras' si está disponible (también con parche)
        try:
            import keras as skkeras  # type: ignore
            self.logger.debug("Intentando cargar modelo con standalone keras (parche temporal InputLayer.from_config)...")
            orig = _patch_inputlayer_from_config(skkeras.layers)
            try:
                self._model = skkeras.models.load_model(str(self.modelo_path), compile=False)
            finally:
                _restore_from_config(skkeras.layers, orig)
            return
        except Exception as e_keras:
            self.logger.warning(f"Standalone keras.models.load_model falló: {e_keras}")

        # Si ambos fallan, intentar lectura HDF5 mínima para dar más contexto (no reconstruye modelo)
        try:
            import h5py
            self.logger.debug("Intentando abrir archivo HDF5 para inspección...")
            with h5py.File(str(self.modelo_path), 'r') as h5f:
                # Extraer información básica para ayuda al usuario
                keys = list(h5f.keys())
                self.logger.debug(f"Contenido HDF5: {keys}")
        except Exception:
            # no necesario fallar aquí, solo información adicional en logs
            pass

        # Si llegamos aquí, no se pudo cargar el modelo con las estrategias conocidas
        raise RuntimeError(
            "No se pudo cargar el modelo con tensorflow.keras ni con keras standalone. "
            "Verifique la versión del modelo y la compatibilidad entre Keras/TensorFlow. "
            "Considere volver a guardar el modelo con tf.keras>=2.10 o convertir el formato."
        )

    @property
    def model(self):
        """Retorna el modelo ya cargado (cargado en __init__)."""
        return self._model

    @property 
    def face_detection(self):
        """Cargar MediaPipe solo cuando sea necesario (perezoso)."""
        if self._face_detection is None:
            try:
                import mediapipe as mp
                self.logger.info("Inicializando MediaPipe...")
                self.mp_face = mp.solutions.face_detection
                self._face_detection = self.mp_face.FaceDetection(
                    model_selection=1, min_detection_confidence=0.5
                )
            except Exception as e:
                self.logger.error(f"Error al inicializar MediaPipe: {e}")
                raise RuntimeError(f"No se pudo inicializar MediaPipe: {e}")
        return self._face_detection

    def __del__(self):
        """Cierra MediaPipe al destruir la instancia si fue inicializado."""
        try:
            if hasattr(self, '_face_detection') and self._face_detection is not None:
                try:
                    self._face_detection.close()
                except Exception:
                    # algunos backends pueden no exponer close; ignorar errores en destructor
                    pass
        except Exception:
            pass

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
            if not results or not getattr(results, "detections", None):
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