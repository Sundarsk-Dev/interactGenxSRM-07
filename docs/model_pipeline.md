# Model Pipeline

1. **Input**: Image + Text (or Audio).
2. **Text-to-Speech (TTS):**
   - Text is normalized.
   - Pyloudnorm or similar normalizes volume.
   - Acoustic model (FastSpeech2) generates mel-spectrogram.
   - Vocoder (HiFi-GAN) generates waveform.
3. **Voice Cloning (Optional):**
   - Reference audio passed to Speaker Encoder.
   - d-vector embedding extracted.
   - Embedding conditioning added to TTS acoustic model.
4. **Lip Sync:**
   - Face detection (dlib/S3FD) finds face bbox.
   - Audio is mel-spectrogram processed.
   - Wav2Lip Generator takes (Face Frames + Audio Mels).
   - Discriminator ensures sync quality (during training).
5. **Post-Processing:**
   - Video resolution enhancement (GFPGAN - optional).
   - Frame interpolation for smoothness.
   - FFmpeg merges audio and video stream.
