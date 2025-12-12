import requests
import os

url = "https://www.w3schools.com/html/mov_bbb.mp4"
output_path = "core_models/lip_sync/sample_video.mp4"

print(f"Downloading sample video from {url}...")
try:
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"Success! Saved to {output_path}")
except Exception as e:
    print(f"Error: {e}")
