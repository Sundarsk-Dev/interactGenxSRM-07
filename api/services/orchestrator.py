from core_models.tts.edge_tts_engine import EdgeTTSEngine
from core_models.lip_sync.wav2lip import Wav2LipEngine
import os
import uuid

class Orchestrator:
    def __init__(self):
        self.tts = EdgeTTSEngine()
        self.lip_sync = Wav2LipEngine()
        
    async def render_pipeline(self, image_path: str, text: str = None, audio_path: str = None, voice_profile_id: str = None):
        session_id = str(uuid.uuid4())
        output_dir = f"storage/sessions/{session_id}"
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Audio Generation (if text provided)
        if text and not audio_path:
            audio_path = os.path.join(output_dir, "speech.wav")
            # In a real app we would load the voice profile here
            self.tts.synthesize(text, audio_path, {"voice_profile": voice_profile_id})
            
        if not audio_path:
            raise ValueError("Either text or audio must be provided")
            
        # 2. Lip Sync Animation
        video_output_path = os.path.join(output_dir, "final_video.mp4")
        self.lip_sync.animate(image_path, audio_path, video_output_path)
        
        return video_output_path, session_id
