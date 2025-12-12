import sys
import os
import torch
import cv2
import numpy as np
import warnings
import moviepy.video.io.ImageSequenceClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import VideoClip
import mediapipe as mp

# Suppress warnings
warnings.filterwarnings("ignore")

# Add the external repo to sys.path
REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "external", "Wav2Lip")
sys.path.append(REPO_ROOT)

try:
    from models import Wav2Lip
    import audio 
except ImportError:
    pass

from core_models.base import LipSyncEngine

class Wav2LipRealEngine(LipSyncEngine):
    def __init__(self, checkpoint_path=None):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.img_size = 96
        
        if checkpoint_path is None:
            checkpoint_path = os.path.join(REPO_ROOT, "checkpoints", "wav2lip_gan.pth")
            
        self.model = self._load_model(checkpoint_path)
        
        # Initialize Mediapipe Face Detection
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

    def _load_model(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Checkpoint not found at {path}. Please run download_weights.py")
            
        model = Wav2Lip()
        checkpoint = torch.load(path, map_location=self.device)
        s = checkpoint["state_dict"]
        new_s = {}
        for k, v in s.items():
            new_s[k.replace('module.', '')] = v
        model.load_state_dict(new_s)
        model = model.to(self.device)
        model.eval()
        return model

    def _get_face_rect(self, image):
        # Convert to RGB
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(img_rgb)
        
        if not results.detections:
            return None
            
        # Get the first face
        detection = results.detections[0]
        bboxC = detection.location_data.relative_bounding_box
        ih, iw, _ = image.shape
        x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
        
        # Wav2Lip expects a square crop roughly centered on the face? 
        # Actually it works best if we crop the face with some padding and resize to 96x96.
        # Crucially, we must preserve aspect ratio or the face distorts.
        
        center_x = x + w // 2
        center_y = y + h // 2
        
        # Determine the size of the square crop
        # Use the maximum dimension of the detection + padding
        max_dim = max(w, h)
        scale = 1.1 # Tighter crop (was 1.25) to improve resolution of lips in 96x96 box
        crop_size = int(max_dim * scale)
        
        # Calculate coordinates ensuring we stay within image bounds?
        # Ideally we pad with black if we go out of bounds, preventing distortion.
        
        x1 = center_x - crop_size // 2
        y1 = center_y - crop_size // 2
        x2 = x1 + crop_size
        y2 = y1 + crop_size
        
        # Adjust if out of bounds (simple clamp might shift center, but safer than crashing)
        # For a truly robust pipeline we would pad the image, but simple clamping is often 'good enough'
        # provided the face isn't right on the edge.
        
        # Let's do a strict square. If it goes out of bounds, we might lose part of the face, 
        # but usually users center their photos.
        
        # However, to be safe, let's just clamp the coords and handle the potential non-squareness
        # or just pad content.
        
        return (x1, y1, x2, y2)

    def _crop_face(self, image, rect):
        x1, y1, x2, y2 = rect
        h, w, c = image.shape
        
        # Calculate padding needed if coords are out of bounds
        pad_l = abs(min(x1, 0))
        pad_t = abs(min(y1, 0))
        pad_r = max(x2 - w, 0)
        pad_b = max(y2 - h, 0)
        
        # Create padded image if needed
        if pad_l > 0 or pad_t > 0 or pad_r > 0 or pad_b > 0:
            image = cv2.copyMakeBorder(image, pad_t, pad_b, pad_l, pad_r, cv2.BORDER_CONSTANT, value=(0,0,0))
            # Shift coords to match padded image
            x1 += pad_l
            y1 += pad_t
            x2 += pad_l
            y2 += pad_t
            
        return image[y1:y2, x1:x2]

    def _sharpen(self, img):
        # Simple sharpening kernel
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        return cv2.filter2D(img, -1, kernel)

    def animate(self, image_path: str, audio_path: str, output_path: str):
        print(f"Starting animate: {image_path} + {audio_path}")
        
        # 1. Load Audio and MEL
        if not os.path.exists(audio_path):
             raise FileNotFoundError(f"Audio not found: {audio_path}")

        # Resample logic handled by repo's audio module usually, but we check
        try:
             wav = audio.load_wav(audio_path, 16000)
             mel = audio.melspectrogram(wav)
        except Exception as e:
             print(f"Error processing audio: {e}")
             raise

        if np.isnan(mel.reshape(-1)).sum() > 0:
            raise ValueError('Mel contains nan!')

        # 2. Prepare Mel Chunks
        mel_chunks = []
        fps = 25
        mel_step_size = 16
        mel_idx_multiplier = 80./fps 
        
        i = 0
        while 1:
            start_idx = int(i * mel_idx_multiplier)
            if start_idx + mel_step_size > len(mel[0]):
                mel_chunks.append(mel[:, len(mel[0]) - mel_step_size:])
                break
            mel_chunks.append(mel[:, start_idx : start_idx + mel_step_size])
            i += 1
            
        print(f"Generated {len(mel_chunks)} audio chunks (video frames).")
            
        # 3. Load Image and Detect Face
        full_frame = cv2.imread(image_path)
        if full_frame is None:
            raise ValueError(f"Could not read image: {image_path}")
            
        face_rect = self._get_face_rect(full_frame)
        if not face_rect:
            # Fallback to center crop if no face detected? Or error?
            print("Warning: No face detected by MediaPipe. Using center crop.")
            h, w = full_frame.shape[:2]
            face_rect = (w//4, h//4, 3*w//4, 3*h//4)
            
        face_img = self._crop_face(full_frame, face_rect)
        # Use Lanczos for downscaling to preserve details
        face_img_resized = cv2.resize(face_img, (self.img_size, self.img_size), interpolation=cv2.INTER_LANCZOS4)
        
        # 4. Inference Loop
        # We need to create a batch of frames (repeated static image)
        # Wav2Lip inputs:
        #   indiv_mels: (B, 1, 80, 16)
        #   x: (B, 6, 96, 96) -> Masked Image + Reference Image concatenated channel-wise
        #      Top half of masked image is 0.
        
        generated_frames = []
        batch_size = 32 # Can increase for GPU
        
        gen_img_input = face_img_resized.copy()
        # Mask lower half
        gen_img_input[self.img_size//2:, :] = 0
        
        # Prepare batch tensors
        # Repeats of the same processed face input
        # Concatenate (Masked, Reference) channel-wise -> 3+3 = 6 channels
        batch_input_img = np.concatenate((gen_img_input, face_img_resized), axis=2) / 255.
        batch_input_img = batch_input_img.transpose(2, 0, 1) # (6, 96, 96)
        batch_input_img = batch_input_img[np.newaxis, ...] # (1, 6, 96, 96)
        
        print("Running inference...")
        
        for i in range(0, len(mel_chunks), batch_size):
            # Get mel batch
            curr_mel_chunks = mel_chunks[i : i+batch_size]
            B = len(curr_mel_chunks)
            
            # Prepare Mels
            input_mels = np.array(curr_mel_chunks) #(B, 80, 16)
            input_mels = input_mels.reshape(B, 1, 80, 16)
            input_mels = torch.FloatTensor(input_mels).to(self.device)
            
            # Prepare Images (Repeat B times)
            input_imgs = np.tile(batch_input_img, (B, 1, 1, 1))
            input_imgs = torch.FloatTensor(input_imgs).to(self.device)
            
            with torch.no_grad():
                # Model returns (B, 3, 96, 96) with values 0-1
                preds = self.model(input_mels, input_imgs)
                
            preds = preds.cpu().numpy().transpose(0, 2, 3, 1) * 255.
            
            # Paste back logic
            for p in preds:
                p = p.astype(np.uint8)
                
                # Resize prediction back to the crop size using Lanczos
                x1, y1, x2, y2 = face_rect
                crop_w = x2 - x1
                crop_h = y2 - y1
                p_resized = cv2.resize(p, (crop_w, crop_h), interpolation=cv2.INTER_LANCZOS4)
                
                # Optional: Mild sharpening to counter blur
                p_resized = self._sharpen(p_resized)
                
                # Soft Face Masking
                mask = np.zeros((crop_h, crop_w), dtype=np.float32)
                
                # Gradient mask: blend from 50% to 80% of the crop height (mouth region)
                blend_start = int(crop_h * 0.5) 
                blend_end = int(crop_h * 0.8)
                
                mask[blend_start:blend_end, :] = np.linspace(0, 1, blend_end - blend_start)[:, None]
                mask[blend_end:, :] = 1.0
                
                # Blur mask for smoothness
                mask = cv2.GaussianBlur(mask, (21, 21), 11)
                
                # Expand to 3 channels
                mask_3c = np.repeat(mask[:, :, np.newaxis], 3, axis=2)
                
                new_frame = full_frame.copy()
                
                # Safe coords logic
                oy1 = max(0, y1); oy2 = min(full_frame.shape[0], y2)
                ox1 = max(0, x1); ox2 = min(full_frame.shape[1], x2)
                
                py1 = max(0, -y1) 
                py2 = py1 + (oy2 - oy1)
                px1 = max(0, -x1)
                px2 = px1 + (ox2 - ox1)
                
                # Regions
                original_roi = new_frame[oy1:oy2, ox1:ox2].astype(np.float32)
                prediction_roi = p_resized[py1:py2, px1:px2].astype(np.float32)
                mask_roi = mask_3c[py1:py2, px1:px2]
                
                # Blend: Result = Original * (1-Mask) + Prediction * Mask
                blended_roi = original_roi * (1.0 - mask_roi) + prediction_roi * mask_roi
                
                new_frame[oy1:oy2, ox1:ox2] = blended_roi.astype(np.uint8)
                generated_frames.append(cv2.cvtColor(new_frame, cv2.COLOR_BGR2RGB))
                
        # 5. Save Video with Audio
        print(f"Saving video to {output_path}")
        clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(generated_frames, fps=fps)
        audio_clip = AudioFileClip(audio_path)
        
        # Trim audio to match video length if needed, or vice-versa
        # Usually we want full audio
        if audio_clip.duration > clip.duration:
             audio_clip = audio_clip.subclipped(0, clip.duration)
             
        final_clip = clip.with_audio(audio_clip)
        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', logger=None)
        
        print("Done.")
        return output_path
