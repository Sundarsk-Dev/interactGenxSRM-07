from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from api.schemas.common import CloneVoiceResponse
import uuid
import os
import shutil

router = APIRouter()

@router.post("/clone-voice", response_model=CloneVoiceResponse)
async def clone_voice_profile(file: UploadFile = File(...)):
    # Save the file
    upload_dir = "storage/voice_samples"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_id = str(uuid.uuid4())
    file_path = os.path.join(upload_dir, f"{file_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    from core_models.voice_cloning.encoder import SpeakerEncoder
    encoder = SpeakerEncoder()
    profile_id = encoder.embed_speaker(file_path)
    
    return CloneVoiceResponse(voice_profile_id=profile_id)
