from faster_whisper import WhisperModel
import os
import torch

class STTEngine:
    def __init__(self, model_size="base", device="cpu"):
        print(f"Loading Whisper STT Model: {model_size} on {device}...")
        compute_type = "int8"
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        print("Whisper Model Loaded.")

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribes audio file to text.
        """
        segments, info = self.model.transcribe(audio_path, beam_size=5, vad_filter=True, vad_parameters=dict(min_silence_duration_ms=500))
        text = " ".join([segment.text for segment in segments])
        return text.strip()

# Singleton instance
_stt_engine = None

def get_stt_engine():
    global _stt_engine
    if _stt_engine is None:
        _stt_engine = STTEngine()
    return _stt_engine
