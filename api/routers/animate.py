from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from api.schemas.common import AnimateResponse
from typing import Optional
import uuid
import os
import shutil

router = APIRouter()

from api.services.orchestrator import Orchestrator

orchestrator = Orchestrator()

@router.post("/render", response_model=AnimateResponse)
async def render_talking_head(
    image: UploadFile = File(...),
    text: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    voice_profile_id: Optional[str] = Form(None),
    consent_confirmed: bool = Form(...)
):
    if not consent_confirmed:
        raise HTTPException(status_code=400, detail="Consent must be confirmed.")

    # Save inputs
    temp_id = str(uuid.uuid4())
    temp_dir = f"storage/temp/{temp_id}"
    os.makedirs(temp_dir, exist_ok=True)
    
    image_path = os.path.join(temp_dir, image.filename or "input.jpg")
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
        
    audio_path = None
    if audio:
        audio_path = os.path.join(temp_dir, audio.filename or "input.wav")
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
            
    # Orchestration Logic
    try:
        video_path, session_id = await orchestrator.render_pipeline(
            image_path=image_path,
            text=text,
            audio_path=audio_path,
            voice_profile_id=voice_profile_id
        )
        # In a real deployed scenario we'd upload to S3 or serve via static
        # For now assume static mounting
        return AnimateResponse(video_url=f"/static/sessions/{session_id}/final_video.mp4")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/animate", response_model=AnimateResponse)
async def animate_face(
    image: UploadFile = File(...),
    audio: UploadFile = File(...),
    consent_confirmed: bool = Form(...)
):
    return await render_talking_head(
        image=image, text=None, audio=audio, voice_profile_id=None, consent_confirmed=consent_confirmed
    )
