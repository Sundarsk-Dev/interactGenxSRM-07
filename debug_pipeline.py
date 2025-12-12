import asyncio
import os
import sys
from api.services.orchestrator import Orchestrator

# Setup paths
if not os.path.exists("storage/temp"):
    os.makedirs("storage/temp")

async def run_debug():
    print("Initializing Orchestrator...")
    try:
        orchestrator = Orchestrator()
    except Exception as e:
        print(f"FAILED to initialize Orchestrator: {e}")
        import traceback
        traceback.print_exc()
        return

    # Use the sample image we know exists or create a dummy one
    test_image = "storage/temp/test_face.jpg"
    if not os.path.exists(test_image):
        # Download a sample face if needed or just use a placeholder
        # For now let's hope the user has something or we can mock it
        # Actually, let's just create a blank black image with a drawn face to be safe
        import cv2
        import numpy as np
        img = np.zeros((512, 512, 3), dtype=np.uint8)
        cv2.circle(img, (256, 256), 100, (255, 255, 255), -1) # face
        cv2.circle(img, (200, 240), 10, (0, 0, 0), -1) # left eye
        cv2.circle(img, (312, 240), 10, (0, 0, 0), -1) # right eye
        cv2.ellipse(img, (256, 300), (40, 20), 0, 0, 180, (0, 0, 0), 5) # mouth
        cv2.imwrite(test_image, img)
        print(f"Created dummy face at {test_image}")

    print("Running render_pipeline...")
    try:
        video_path, session_id = await orchestrator.render_pipeline(
            image_path=test_image,
            text="Hello, this is a test of the emergency broadcast system.",
            voice_profile_id="en-US-ChristopherNeural"
        )
        print(f"SUCCESS! Video generated at: {video_path}")
    except Exception as e:
        print(f"FAILED during pipeline execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_debug())
