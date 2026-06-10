# AGRIOT UX - Emotion Analysis for UX Interviews

<p align="center">
  <img src="img/mascota_agriot.png" width="220" alt="AGRIOT mascot">
</p>

Desktop research platform for capturing UX interviews, segmenting them by question, running facial-emotion analysis offline, and exporting actionable reports.

<p>
  <img src="https://img.shields.io/badge/Python-Desktop%20App-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PySide6-Qt%20GUI-41CD52?style=flat-square&logo=qt&logoColor=white" alt="PySide6">
  <img src="https://img.shields.io/badge/TensorFlow-CNN%20Inference-FF6F00?style=flat-square&logo=tensorflow&logoColor=white" alt="TensorFlow">
  <img src="https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?style=flat-square&logo=opencv&logoColor=white" alt="OpenCV">
  <img src="https://img.shields.io/badge/MediaPipe-Face%20Detection-009688?style=flat-square&logo=google&logoColor=white" alt="MediaPipe">
  <img src="https://img.shields.io/badge/FFmpeg-Video%20Processing-007808?style=flat-square" alt="FFmpeg">
</p>

## Overview

AGRIOT UX was built to support UX research in rural and agricultural contexts where researchers need a practical, offline-friendly workflow for interview capture and emotional analysis.

The system records interviews, lets the researcher mark the beginning and end of each question, automatically cuts the video into question-based fragments, runs facial-emotion inference with a CNN model, and produces structured outputs for later analysis and reporting.

## Why This Project Matters

- It solves a real research workflow instead of only showcasing a model.
- It connects product thinking, desktop software, computer vision, and reporting into one usable application.
- It is designed for constrained environments where offline execution matters.

## Core Capabilities

- Full interview capture with video and audio
- Time-based question marking during the session
- Automatic video fragmentation per question
- CNN-based facial emotion analysis
- Face detection with MediaPipe before inference
- Exportable reports and traceable output files
- Embedded visual controls through Qt and web components

## End-to-End Workflow

1. Record a UX interview from the desktop app.
2. Mark question boundaries as the session progresses.
3. Save structured interview metadata and question annotations.
4. Split the original recording into per-question video fragments.
5. Run offline facial-emotion analysis on those fragments.
6. Review dominant emotions and aggregated metrics in reports.

## Emotion Analysis Pipeline

- Input video is processed frame by frame.
- Faces are detected with MediaPipe.
- Cropped facial regions are normalized and passed to a TensorFlow / Keras model.
- The system predicts seven emotions:
  - `angry`
  - `contempt`
  - `disgust`
  - `fear`
  - `happy`
  - `sad`
  - `surprise`
- The app computes average intensities and identifies dominant emotions for each fragment.

## Tech Stack

### Desktop and UI

- `PySide6`
- `QtWidgets`
- `QtWebEngine`
- `QWebChannel`

### AI and computer vision

- `TensorFlow / Keras`
- `OpenCV`
- `MediaPipe`
- `NumPy`

### Video and reporting

- `FFmpeg`
- `fpdf2`
- JSON-based metadata outputs

## Repository Structure

```text
classes/
  analisis.py
  entrevista.py
  entrevista_preguntas.py
  fragmento.py
  marca.py
  marcas.py
  reporte.py
  reporte_entrevista.py
ui/
  app.py
  interview_screen.py
  interviewee_screen.py
  config_screen.py
  analisis_screen.py
  reportes_screen.py
video_io/
  video.py
ml/
  cp_best.keras
  cp_best_finetuned.keras
main.py
```

## Architecture Snapshot

### Capture layer

- Handles audiovisual interview recording
- Streams preview data to the interface
- Persists original recordings and related metadata

### Annotation layer

- Registers start and end marks for each question
- Associates notes and question IDs with interview segments

### Processing layer

- Cuts videos into fragments with FFmpeg
- Runs asynchronous emotion analysis so the UI stays responsive

### Reporting layer

- Aggregates emotional metrics
- Organizes results by interview and fragment
- Supports export-friendly outputs

## Run Locally

### Requirements

- Python `3.8` to `3.10`
- `ffmpeg` installed and available in your PATH
- Camera and microphone permissions enabled

### Install

```bash
git clone https://github.com/yojr23/Proyecto_vision-artificial-para-deteccion-de-emociones-en-entrevistas-ux.git
cd Proyecto_vision-artificial-para-deteccion-de-emociones-en-entrevistas-ux
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-ml.txt
```

### Start the app

```bash
python main.py
```

## Outputs

The project generates and uses structured assets such as:

- Original interview videos
- Question-mark JSON files
- Video fragments per question
- Emotion-analysis results
- Logs for traceability
- Report-ready summaries

## What This Project Demonstrates

- Desktop application engineering with Python and Qt
- Real integration of ML inference into a user-facing product
- Asynchronous processing in a GUI environment
- Offline-first workflow design
- Practical computer vision for research operations

## Ideal Portfolio Positioning

This project is a strong example of:

- AI applied to a concrete domain problem
- Product thinking beyond model training
- Research tooling with operational value
- End-to-end ownership across UX, data flow, inference, and reporting