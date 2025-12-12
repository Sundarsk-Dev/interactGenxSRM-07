from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import yaml
import os

# Load Configuration
def load_config():
    config_path = os.path.join("config", "settings.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}

config = load_config()

app = FastAPI(
    title=config.get("app_name", "InteractGEN"),
    description="Text-to-Speech & Talking Head API",
    version=config.get("version", "1.0.0"),
)

from api.middleware import ContentSafetyMiddleware

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ContentSafetyMiddleware)

from api.routers import tts, voice_cloning, animate

app.include_router(tts.router, prefix="/v1", tags=["Text to Speech"])
app.include_router(voice_cloning.router, prefix="/v1", tags=["Voice Cloning"])
app.include_router(animate.router, prefix="/v1", tags=["Animation"])

from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="storage"), name="static")

@app.get("/health")
def health_check():
    return {"status": "ok", "version": config.get("version")}

if __name__ == "__main__":
    uvicorn.run(
        "api.server:app",
        host=config.get("server", {}).get("host", "0.0.0.0"),
        port=config.get("server", {}).get("port", 8000),
        reload=True
    )
