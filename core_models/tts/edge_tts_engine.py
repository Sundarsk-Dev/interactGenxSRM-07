from core_models.base import TTSEngine
import edge_tts
import asyncio

class EdgeTTSEngine(TTSEngine):
    def synthesize(self, text: str, output_path: str, options: dict) -> str:
        """
        Synthesizes speech using Microsoft Edge's Neural TTS.
        Blocks until completion (uses asyncio.run internally).
        """
        voice = options.get("voice_profile", "en-US-ChristopherNeural")
        if not voice:
            # Fallback to a good default if None provided
            voice = "en-US-ChristopherNeural"
            
        print(f"Synthesizing '{text[:20]}...' with {voice}")
        
        async def _run_tts():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)

        try:
            asyncio.run(_run_tts())
        except Exception as e:
            # Fallback for already running event loops (e.g. inside uvicorn specific contexts)
            # though asyncio.run usually creates a new one. 
            # If called from async context, user should await specific async method, 
            # but our base class interface is sync.
            import nest_asyncio
            nest_asyncio.apply()
            asyncio.run(_run_tts())
            
        return output_path
