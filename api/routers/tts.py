from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from api.schemas.common import TTSRequest, TTSResponse
import uuid
import os
import shutil

router = APIRouter()

from core_models.tts.edge_tts_engine import EdgeTTSEngine

tts_engine = EdgeTTSEngine()

@router.post("/tts", response_model=TTSResponse)
async def generate_speech(request: TTSRequest):
    output_filename = f"{uuid.uuid4()}.wav"
    output_path = os.path.join("storage/outputs", output_filename)
    os.makedirs("storage/outputs", exist_ok=True)
    
    tts_engine.synthesize(request.text, output_path, request.dict())
    
    return TTSResponse(
        audio_url=f"/static/outputs/{output_filename}", 
        duration=5.0,
        visemes=[{"time": 0.1, "value": "A"}, {"time": 0.2, "value": "B"}]
    )
