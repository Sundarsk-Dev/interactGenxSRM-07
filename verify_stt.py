import os
import sys

print("1. Importing core_models.stt.whisper_engine...")
try:
    from core_models.stt.whisper_engine import get_stt_engine
    print("   Import successful.")
except ImportError as e:
    print(f"   Import FAILED: {e}")
    sys.exit(1)

print("2. Initializing STT Engine (this may download model)...")
try:
    stt = get_stt_engine()
    print("   Initialization successful.")
except Exception as e:
    print(f"   Initialization FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("3. Creating dummy audio file...")
dummy_path = "storage/test_audio.txt" # Whisper will fail on processing, but we check if it runs
# We need a valid audio file to really test transcribe.
# Let's try to just load model for now, that's the biggest hurdle.

print("   Done.")
