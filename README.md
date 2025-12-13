# InteractGEN - Advanced AI Agent System 🤖✨

**InteractGEN** is a cutting-edge multimodal AI agent platform that combines **Talking Heads**, **Voice Interaction**, and **Desktop Automation**. It features a transparent desktop overlay that acts as your personal virtual guide, capable of understanding speech, analyzing your screen, and controlling applications.

🔗 **Repository:** [Sundarsk-Dev/interactGenxSRM-07](https://github.com/Sundarsk-Dev/interactGenxSRM-07)

---

## 🚀 Key Features

*   **🗣️ Real-Time Interaction**: Speak naturally to the agent. It listens (VAD), understands (LLM), and responds with a synchronized talking avatar (TTS + LipSync).
*   **👁️ Visual Intelligence**: Ask *"What is on my screen?"* or *"Where is the start button?"*. The agent uses **Gemini 1.5 Vision** to analyze and highlight UI elements.
*   **🖱️ Desktop Automation**: Commands like *"Open VS Code and clone this repo"* are executed instantly using local system control (Git, Browser, Shell).
*   **⚡ High Performance**:
    *   **English-Only Enforced STT**: Fast and accurate transcription using `faster-whisper`.
    *   **Instant Caching**: Pre-generated responses for common phrases ("Sure", "On it") for <200ms latency.
    *   **Optimized Pipeline**: Parallel processing of Audio and Animation.

---

## 🛠️ Architecture & Tech Stack

The system is built on a modular architecture separating the Brain (API) from the Body (Overlay).

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend API** | **FastAPI (Python)** | High-performance async server managing models and logic. |
| **Frontend UI** | **React / Django** | Web dashboard and "Virtual Guide" overlay script. |
| **LLM & Vision** | **Gemini 1.5 Flash** | Intent parsing and screen analysis. |
| **Speech-to-Text** | **Faster-Whisper** | Local, privacy-focused speech recognition. |
| **Text-to-Speech** | **EdgeTTS** | Natural sounding neural voices. |
| **Lip Sync** | **Wav2Lip** | GAN-based lip synchronization for the avatar. |

---

## 📦 Installation Guide

### Prerequisites
*   **Python 3.10+** (Ensure added to PATH)
*   **Node.js 18+** (For frontend tooling)
*   **Git** (For version control)
*   **Gemini API Key** (Get from [Google AI Studio](https://aistudio.google.com/))

### 1. Clone the Repository
```bash
git clone https://github.com/Sundarsk-Dev/interactGenxSRM-07
cd interactGenxSRM-07
```

### 2. Backend Setup
Set up the Python environment and dependencies.

```bash
# Create virtual environment (Optional but Recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt
```
*Note: If `requirements.txt` is missing, run: `pip install fastapi uvicorn google-generativeai pyautogui python-multipart python-dotenv requests sqlalchemy faster-whisper edge-tts`*

**Configuration:**
Create a `.env` file in the root directory:
```ini
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Frontend / Overlay Setup
To run the web dashboard or overlay integration:

```bash
# Navigate to AtomxAI component (or relevant frontend folder)
cd AtomxAI
# Ensure you serve the static assets correctly.
# If using the React App source:
# cd ../frontend/react-app && npm install
```

---

## ▶️ How to Run

You need to run the **Backend** to power the intelligence.

**Start the Server:**
```bash
# From the root directory (where api/ folder is)
python api/server.py
```
*Server will start at `http://localhost:8000`*

**Using the Agent:**
1.  Open the provided **Web Dashboard** (e.g., `dashboard.html` or the hosted Django app).
2.  Click the **Robot Icon (🤖)** to open the overlay.
3.  Click the **Mic (🎤)** and speak!

---

## 🗣️ Example Commands

*   **Automation**: *"Clone this repository in my Downloads folder"*
*   **Navigation**: *"Open Youtube"*, *"Go to github.com"*
*   **Vision**: *"Where is the login button?"* (Agent highlights it)
*   **General**: *"Read this page for me"*, *"Sign me up"*

---

## 🤝 Contributing
1.  Fork the repo.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---
*Built with ❤️ by the AtomX AI Team*