import React, { useState } from 'react';
import VirtualGuide from './components/VirtualGuide';
import axios from 'axios';

const API_BASE = "http://localhost:8000/v1";

function App() {
    const [image, setImage] = useState(null);
    const [text, setText] = useState("");
    const [loading, setLoading] = useState(false);
    const [videoUrl, setVideoUrl] = useState(null);
    const [consent, setConsent] = useState(false);
    const [error, setError] = useState(null);

    const handleImageUpload = (e) => {
        if (e.target.files && e.target.files[0]) {
            setImage(e.target.files[0]);
        }
    };

    const handleGenerate = async () => {
        if (!image || !text) {
            setError("Please provide both an image and text.");
            return;
        }
        if (!consent) {
            setError("You must confirm consent to animate this face.");
            return;
        }

        setLoading(true);
        setError(null);
        setVideoUrl(null);

        const formData = new FormData();
        formData.append('image', image);
        formData.append('text', text);
        formData.append('consent_confirmed', 'true');

        try {
            const response = await axios.post(`${API_BASE}/render`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            // The backend returns a relative URL usually, assume we need to prepend hostname if not full
            // But based on our mock, it returns /static/...
            setVideoUrl(`http://localhost:8000${response.data.video_url}`);
        } catch (err) {
            console.error(err);
            setError("Failed to generate video. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <header className="header">
                <div className="logo">InteractGEN</div>
                <div style={{ color: 'var(--text-secondary)' }}>v1.0.0</div>
            </header>

            <div className="main-grid">
                <div className="card input-section">
                    <h2>Create Talking Head</h2>

                    <div className="input-group">
                        <label>1. Upload Portrait Image</label>
                        <div className="file-drop" onClick={() => document.getElementById('fileInput').click()}>
                            {image ? image.name : "Click to upload an image"}
                            <input
                                id="fileInput"
                                type="file"
                                accept="image/*"
                                onChange={handleImageUpload}
                                style={{ display: 'none' }}
                            />
                        </div>
                    </div>

                    <div className="input-group">
                        <label>2. Enter Text to Speak</label>
                        <textarea
                            rows="4"
                            placeholder="Hello, I am an AI generated avatar..."
                            value={text}
                            onChange={(e) => setText(e.target.value)}
                        />
                    </div>

                    <div className="consent-check">
                        <input
                            type="checkbox"
                            id="consent"
                            checked={consent}
                            onChange={(e) => setConsent(e.target.checked)}
                        />
                        <label htmlFor="consent" style={{ marginBottom: 0 }}>
                            I confirm I have the rights to use this image and content.
                        </label>
                    </div>

                    {error && <div style={{ color: '#ef4444', marginBottom: '1rem' }}>{error}</div>}

                    <button
                        className="btn-primary"
                        onClick={handleGenerate}
                        disabled={loading || !image || !text || !consent}
                    >
                        {loading ? "Generating..." : "Generate Video"}
                    </button>
                </div>

                <div className="card preview-section">
                    <h2>Preview</h2>
                    <div className="preview-area">
                        {loading && (
                            <div className="loading-overlay">
                                <div className="spinner"></div>
                                <p>Synthesizing voice & lip-syncing...</p>
                            </div>
                        )}

                        {!loading && videoUrl && (
                            <video src={videoUrl} controls autoPlay />
                        )}

                        {!loading && !videoUrl && (
                            <div style={{ color: 'var(--text-secondary)', textAlign: 'center' }}>
                                Generated video will appear here.
                            </div>
                        )}
                    </div>
                </div>
            </div>
            {/* Virtual Guide Widget */}
            <VirtualGuide />
        </div>
    );
}

export default App;
