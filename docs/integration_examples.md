# Integration Examples

## JavaScript / Node.js
Using the standard `axios` library or our SDK.

```javascript
import { Client } from 'interactgen-sdk';

const client = new Client("http://localhost:8000/v1");

// 1. Text to Speech
const audio = await client.tts("Hello world", { emotion: "happy" });
console.log("Audio URL:", audio.audio_url);

// 2. Full Talking Head Render
const videoUrl = await client.render({
  imagePath: "./avatar.jpg",
  text: "Welcome to our platform.",
  voiceProfileId: "user-123"
});
document.getElementById("video").src = videoUrl;
```

## Python
Using the Python SDK.

```python
from interactgen_sdk import Client

client = Client(base_url="http://localhost:8000/v1")

# 1. Clone a voice
profile = client.clone_voice("my_voice_sample.wav")
profile_id = profile["voice_profile_id"]

# 2. Generate Video
video_url = client.render(
    image_path="face.jpg",
    text="This is my cloned voice speaking.",
    voice_profile_id=profile_id
)
print(f"Video generated at: {video_url}")
```

## cURL (Raw API)

**Generate TTS:**
```bash
curl -X POST "http://localhost:8000/v1/tts" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello world", "language": "en"}'
```

**Animate:**
```bash
curl -X POST "http://localhost:8000/v1/animate" \
     -F "image=@face.jpg" \
     -F "audio=@speech.wav" \
     -F "consent_confirmed=true"
```
