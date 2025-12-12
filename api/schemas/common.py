from pydantic import BaseModel, Field
from typing import Optional, List, Dict

# --- Shared ---
class ResponseBase(BaseModel):
    status: str = "success"
    message: Optional[str] = None

# --- TTS ---
class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech", min_length=1)
    voice_profile_id: Optional[str] = Field(None, description="ID of a cloned voice profile")
    language: str = Field("en", description="Language code")
    speed: float = Field(1.0, description="Speech speed")
    pitch: float = Field(1.0, description="Speech pitch")
    emotion: Optional[str] = Field("neutral", description="Emotion style")

class TTSResponse(ResponseBase):
    audio_url: str
    duration: float
    visemes: Optional[List[Dict]] = None # Timestamped visemes

# --- Voice Cloning ---
class CloneVoiceResponse(ResponseBase):
    voice_profile_id: str

# --- Animate ---
class AnimateRequest(BaseModel):
    image_url: Optional[str] = None # Or base64? Let's assume URL or file upload handled separately
    audio_url: Optional[str] = None
    voice_profile_id: Optional[str] = None
    text: Optional[str] = None # If audio is not provided
    
    # Flags
    consent_confirmed: bool = Field(..., description="User MUST confirm they have rights to use this image")
    
class AnimateResponse(ResponseBase):
    video_url: str
    metadata: Optional[Dict] = None

# --- Render (Orchestrator) ---
class RenderRequest(AnimateRequest):
    pass # Same as animate essentially, but explicitly for the full pipeline

class RenderResponse(AnimateResponse):
    pass
