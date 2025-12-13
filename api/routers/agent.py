from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
from api.services.agent_service import AgentService
from api.services.orchestrator import Orchestrator
import os

router = APIRouter()
agent_service = AgentService()
orchestrator = Orchestrator()

class AgentRequest(BaseModel):
    text: str
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    render: Optional[Dict[str, Any]] = None
    action: Optional[Dict[str, Any]] = None
    transcript: Optional[str] = None

@router.post("/parse", response_model=AgentResponse)
async def parse_agent_request(req: AgentRequest):
    try:
        # 1. Parse Intent (Mock Gemini)
        response_payload = await agent_service.parse_intent(req.text, req.context)
        
        # 2. If 'render' instruction exists and TTS is requested, execute Visual Pipeline
        render = response_payload.get("render")
        if render and render.get("tts"):
            text_to_speak = render.get("text")
            voice = render.get("voice", "en-US-ChristopherNeural")
            avatar_id = render.get("avatar_image_id", "male_business_portrait_v1")
            
            # Resolve avatar path (assuming it's in public assets or we need the source for Wav2Lip)
            # Wav2Lip needs a local file path. 
            # We copied the asset to frontend/react-app/public/assets/male_business_portrait_v1.png
            # We should validly check where this file is relative to the backend.
            # Relative to backend root (InteractGEN):
            avatar_path = os.path.abspath(f"frontend/react-app/public/assets/{avatar_id}.png")
            
            if not os.path.exists(avatar_path):
                 # Fallback code if the specific asset isn't found, maybe use a default or error
                 # For now, let's assume it exists as we copied it.
                 pass
            
            # Run Orchestrator Pipeline
            # Note: This is a synchronous block that waits for generation. 
            # Ideally we'd optimize latency (stream audio first?), but strict requirement is LIP SYNC.
            # Run Orchestrator Pipeline
            video_path, session_id = await orchestrator.render_pipeline(
                image_path=avatar_path,
                text=text_to_speak,
                voice_profile_id=voice,
                session_id=render.get("session_id")
            )
            
            # Return URL to the generated video
            # The frontend expects 'video_base64' in the sample, but implies 'video_blob' logic.
            # We will return a URL for better performance and let the frontend load it.
            # However, to support the simplified sample code provided by the user (which checks video_base64),
            # we might need to adapt. But sending 2-MB video base64 in JSON is bad.
            # Let's send 'video_url' and update the frontend to handle it.
            
            render["video_url"] = f"http://localhost:8000/static/sessions/{session_id}/final_video.mp4"
            render["audio_url"] = f"http://localhost:8000/static/sessions/{session_id}/speech.wav"
            
            # Clean up base64 keys if they were placeholder
            # render.pop("video_base64", None) # Not removing, just not adding.
            
        return response_payload
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import UploadFile, File, Form
from core_models.stt.whisper_engine import get_stt_engine
import shutil
import uuid
import json

@router.post("/audio", response_model=AgentResponse)
async def handle_audio_agent(
    audio: UploadFile = File(...),
    context: str = Form(default="{}") 
):
    try:
        # 1. Save Audio
        session_id = str(uuid.uuid4())
        audio_path = f"storage/temp_{session_id}.webm" 
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
            
        file_size = os.path.getsize(audio_path)
        print(f"Received Audio: {audio_path} | Size: {file_size} bytes")
        
        if file_size < 1000:
             print("WARNING: Audio file is too small/empty.")
            
        # 2. Transcribe (Backend STT)
        stt = get_stt_engine()
        transcribed_text = stt.transcribe(audio_path)
        print(f"Transcribed: {transcribed_text}")
        
        # Cleanup audio
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
        if not transcribed_text:
             # Just return empty if silence, or error
             return AgentResponse(render={
                 "type": "render", 
                 "text": "I didn't catch that.", 
                 "tts": True,
                 "session_id": "generic_confusion"
             })

        # 3. Parse Intent
        print(f"Context raw: {context}")
        try:
            ctx = json.loads(context)
        except Exception as json_err:
            print(f"JSON Parse Error: {json_err}")
            ctx = {}
            
        print(f"Parsing intent for: {transcribed_text}")
        response_payload = await agent_service.parse_intent(transcribed_text, ctx)
        print(f"Intent Payload: {response_payload}")
        
        # 4. Render Pipeline (Copy of logic above)
        render = response_payload.get("render")
        if render and render.get("tts"):
            text_to_speak = render.get("text")
            voice = render.get("voice", "en-US-ChristopherNeural")
            avatar_id = render.get("avatar_image_id", "male_business_portrait_v1")
            
            avatar_path = os.path.abspath(f"frontend/react-app/public/assets/{avatar_id}.png")
            
            video_path, session_id = await orchestrator.render_pipeline(
                image_path=avatar_path,
                text=text_to_speak,
                voice_profile_id=voice,
                session_id=render.get("session_id")
            )
            
            render["video_url"] = f"http://localhost:8000/static/sessions/{session_id}/final_video.mp4"
            render["audio_url"] = f"http://localhost:8000/static/sessions/{session_id}/speech.wav"
            
        # Add transcript to response
        response_payload["transcript"] = transcribed_text
        return response_payload

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
