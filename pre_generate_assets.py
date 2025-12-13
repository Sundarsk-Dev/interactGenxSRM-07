import asyncio
import os
import sys

# Add root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.services.orchestrator import Orchestrator

# Pre-defined generic responses
# ID -> Text
PREDEFINED_RESPONSES = {
    "generic_sure": "Sure, I can do that.",
    "generic_on_it": "Sure, on it.",
    "generic_which_dir": "Which directory should I use?",
    "generic_cant_do": "I can't do that right now.",
    "generic_working": "Working on it.",
    "generic_done": "Done.",
    "generic_understood": "Understood.",
    "generic_searching": "Searching for that.",
    "generic_opening": "Opening that for you.",
    "generic_listening": "I'm listening.",
    "generic_thinking": "Let me think about that.",
    "generic_confusion": "I didn't catch that.",
    "vision_analyzing": "Analyzing the screen, please wait.",
    "navigation_going_home": "Going Home.",
    "navigation_dashboard": "Taking you to your Dashboard.",
    "auth_login": "Okay, opening the login screen."
}

AVATAR_PATH = os.path.abspath("frontend/react-app/public/assets/male_business_portrait_v1.png")
VOICE = "en-US-ChristopherNeural"

async def generate_assets():
    if not os.path.exists(AVATAR_PATH):
        print(f"Error: Avatar not found at {AVATAR_PATH}")
        return

    orchest = Orchestrator()
    
    print(f"Starting Pre-generation for {len(PREDEFINED_RESPONSES)} items...")
    
    for session_id, text in PREDEFINED_RESPONSES.items():
        print(f"Generating: [{session_id}] -> '{text}'")
        try:
            # We enforce the session_id to match our key
            # This creates storage/sessions/generic_sure/final_video.mp4
            video_path, _ = await orchest.render_pipeline(
                image_path=AVATAR_PATH,
                text=text,
                voice_profile_id=VOICE,
                session_id=session_id
            )
            print(f"  -> Generated at: {video_path}")
        except Exception as e:
            print(f"  -> FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(generate_assets())
