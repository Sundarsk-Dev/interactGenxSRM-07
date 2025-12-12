import requests
import os
import sys

def download_file(url, str_path):
    print(f"Downloading {os.path.basename(str_path)}...")
    os.makedirs(os.path.dirname(str_path), exist_ok=True)
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(str_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192): 
                f.write(chunk)
        print("Done.")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

# Base paths
repo_root = "core_models/lip_sync/external/Wav2Lip"
checkpoints_dir = os.path.join(repo_root, "checkpoints")
face_det_dir = os.path.join(repo_root, "face_detection", "detection", "sfd")

# URLs (using HuggingFace mirror for stability)
wav2lip_gan_url = "https://huggingface.co/camenduru/Wav2Lip/resolve/main/checkpoints/wav2lip_gan.pth"
s3fd_url = "https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth"

if __name__ == "__main__":
    download_file(wav2lip_gan_url, os.path.join(checkpoints_dir, "wav2lip_gan.pth"))
    download_file(s3fd_url, os.path.join(face_det_dir, "s3fd.pth"))
