from abc import ABC, abstractmethod
import os

class TTSEngine(ABC):
    @abstractmethod
    def synthesize(self, text: str, output_path: str, options: dict):
        """Convert text to audio file."""
        pass

class LipSyncEngine(ABC):
    @abstractmethod
    def animate(self, image_path: str, audio_path: str, output_path: str):
        """Generate a video of the face in image_path speaking the audio_path."""
        pass

class VoiceCloningEngine(ABC):
    @abstractmethod
    def embed_speaker(self, audio_path: str) -> str:
        """Process reference audio and return a speaker embedding ID/Path."""
        pass
