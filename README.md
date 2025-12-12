# InteractGEN: Real-Time Talking Head Generation

InteractGEN is a modular, full-stack application that converts text into high-quality speech and animates a static portrait image to lip-sync with the generated audio. It uses state-of-the-art AI models for realistic output.

![UI Screenshot](https://placehold.co/600x400?text=InteractGEN+UI)

## 🚀 Features

- **High-Quality TTS**: Uses **Microsoft Edge Neural TTS** for natural, human-like voice synthesis.
- **Deepfake Lip-Sync**: Powered by **Wav2Lip GAN** with custom post-processing:
  - **Robust Face Detection**: Uses MediaPipe with optimized square cropping.
  - **High-Res Preservation**: Implements smart gradient masking to blend animated lips with the original high-definition face (preventing full-face pixelation).
  - **Sharpening & Interpolation**: Uses Lanczos4 and sharpening kernels for crisp details.
- **Modern UI**: A premium, dark-mode React frontend for easy interaction.
- **FastAPI Backend**: Asynchronous, scalable Python backend.

## 🛠️ Tech Stack

- **Frontend**: React, Vite, Tailwind-style CSS.
- **Backend**: FastAPI, Uvicorn.
- **AI/ML**: PyTorch, OpenCV, MediaPipe, EdgeTTS.
- **Video Processing**: MoviePy, FFmpeg.

## 📦 Installation

### Prerequisites
- Python 3.10+
- Node.js 16+
- GPU (CUDA) recommended for fast inference (CPU supported but slower).

### 1. Clone the Repository
```bash
git clone https://github.com/nayan2soni/text-to-speach-model.git
cd text-to-speach-model
```

### 2. Backend Setup
```bash
# Install Python dependencies
python -m pip install -r config/requirements.txt

# Download Initial Weights (Wav2Lip + Face Detector)
python download_weights.py
```

### 3. Frontend Setup
```bash
cd frontend/react-app
npm install
cd ../..
```

## ▶️ Usage

### Running Locally (Manual)

**Terminal 1 (Backend):**
```bash
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend/react-app
npm run dev
```

Access the UI at: **http://localhost:5173**

## 🧩 Architecture

The system follows a modular pipeline:
1.  **Input**: User uploads an image and enters text.
2.  **TTS**: Text is converted to audio (`speech.wav`).
3.  **Preprocessing**: Face is detected, cropped (1.1x scale), and resized to 96x96.
4.  **Inference (Wav2Lip)**: The GAN generates lip-synced frames based on audio features (Mel Spectrogram).
5.  **Post-Processing**: Generated lips are masked and blended back into the original high-res image.
6.  **Muxing**: Audio and video are combined using MoviePy.
7.  **Output**: Final MP4 is served to the frontend.

## 📄 License
MIT
