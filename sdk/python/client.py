import requests
import os

class Client:
    def __init__(self, base_url="http://localhost:8000/v1", api_key=None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def tts(self, text, options=None):
        """Convert text to speech."""
        url = f"{self.base_url}/tts"
        payload = {"text": text, **(options or {})}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def clone_voice(self, audio_path):
        """Clone a voice from an audio file."""
        url = f"{self.base_url}/clone-voice"
        with open(audio_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, files=files)
        response.raise_for_status()
        return response.json()

    def render(self, image_path, text, voice_profile_id=None):
        """Full pipeline: Text -> Audio -> Video."""
        url = f"{self.base_url}/render"
        
        # Prepare multipart/form-data
        files = {
            "image": open(image_path, "rb"),
        }
        data = {
            "text": text,
            "voice_profile_id": voice_profile_id,
            "consent_confirmed": "true" # Python requests handles bools oddly in data sometimes
        }
        
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        return response.json()["video_url"]
