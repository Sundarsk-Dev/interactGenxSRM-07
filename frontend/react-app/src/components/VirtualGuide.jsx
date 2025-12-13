import React, { useState, useRef, useEffect } from "react";

export default function VirtualGuide({ apiBase = "http://localhost:8000" }) {
    const [open, setOpen] = useState(false);
    const [listening, setListening] = useState(false);
    const [transcript, setTranscript] = useState("");
    const [busy, setBusy] = useState(false);
    const audioRef = useRef();

    // Auto-scroll transcript
    const transcriptRef = useRef(null);
    useEffect(() => {
        if (transcriptRef.current) {
            transcriptRef.current.scrollTop = transcriptRef.current.scrollHeight;
        }
    }, [transcript]);

    async function sendTextToAgent(text) {
        setBusy(true);
        setTranscript(prev => prev + "\nUser: " + text); // Optimistic update

        try {
            const res = await fetch(`${apiBase}/agent/parse`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text, context: { current_page: window.location.pathname } }),
            });
            const body = await res.json();

            // Handle Render (Visual Response)
            if (body.render) {
                setTranscript(prev => prev + "\nAgent: " + body.render.text);

                // Handle Stop command
                if (body.render.stop_playback) {
                    if (audioRef.current) {
                        audioRef.current.pause();
                        audioRef.current.currentTime = 0;
                    }
                    const videoEl = document.getElementById("vg-video");
                    if (videoEl) videoEl.pause();
                }

                // Handle Video URL (Backend returns URL instead of heavy Base64)
                if (body.render.video_url) {
                    const videoEl = document.getElementById("vg-video");
                    if (videoEl) {
                        videoEl.src = body.render.video_url;
                        videoEl.style.display = "block";
                        videoEl.play().catch(e => console.warn("Autoplay blocked:", e));

                        // Sync audio (video has audio muxed usually, but if separated:)
                        // if (body.render.audio_url) ...

                        videoEl.onended = () => {
                            // Reset to idle state or loop idle video?
                            // For now just pause on last frame
                        };
                    }
                }
            }

            // Handle Actions
            if (body.action) {
                if (body.action.confirmation_required) {
                    // Simple confirm for demo
                    if (confirm(`Virtual Guide wants to ${body.action.action_type}. Allow?`)) {
                        executeAction(body.action);
                    }
                } else {
                    executeAction(body.action);
                }
            }
        } catch (err) {
            console.error("Agent Error:", err);
            setTranscript(prev => prev + "\nError: Could not reach agent.");
        } finally {
            setBusy(false);
        }
    }

    function executeAction(action) {
        console.log("Executing Action:", action);
        if (action.action_type === "fill_form") {
            // Demo specific logic for InteractGEN App.jsx fields if any
            // Or generic selector logic
            if (action.payload) {
                alert(`Form Filled with: ${JSON.stringify(action.payload)}`);
            }
        }
        if (action.action_type === "navigate") {
            window.location.href = action.payload.route;
        }
    }

    return (
        <>
            {/* Floating Toggle Button */}
            <button
                className="fixed bottom-6 right-6 z-50 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full p-4 shadow-lg transition-transform hover:scale-105"
                onClick={() => setOpen(!open)}
            >
                {open ? "✕" : "🤖"}
            </button>

            {/* Guide Interface */}
            {open && (
                <div className="fixed bottom-20 right-6 w-80 bg-white dark:bg-gray-800 rounded-xl shadow-2xl flex flex-col overflow-hidden border border-gray-200 dark:border-gray-700 z-50 animate-fade-in-up">

                    {/* Header */}
                    <div className="bg-gray-100 dark:bg-gray-900 p-3 flex items-center justify-between border-b dark:border-gray-700">
                        <div className="flex items-center">
                            <img src="/assets/male_business_portrait_v1.png" alt="guide" className="w-10 h-10 rounded-full object-cover border-2 border-indigo-500" />
                            <div className="ml-3">
                                <div className="text-sm font-bold text-gray-800 dark:text-gray-100">AtomXAI Guide</div>
                                <div className="text-xs text-green-500 flex items-center">
                                    <span className="w-2 h-2 bg-green-500 rounded-full mr-1"></span> Online
                                </div>
                            </div>
                        </div>
                        {/* Busy Indicator */}
                        {busy && <div className="text-indigo-500 animate-pulse text-xs font-bold">Thinking...</div>}
                    </div>

                    {/* Video / Avatar Area */}
                    <div className="relative w-full aspect-video bg-black flex items-center justify-center overflow-hidden">
                        {/* Default Static Avatar Background */}
                        <img
                            src="/assets/male_business_portrait_v1.png"
                            className="absolute inset-0 w-full h-full object-cover opacity-50"
                            style={{ display: busy || document.getElementById('vg-video')?.paused ? 'block' : 'none' }}
                        />

                        {/* Active Video Overlay */}
                        <video
                            id="vg-video"
                            className="w-full h-full object-cover z-10"
                            playsInline
                            style={{ display: 'none' }}
                        />
                    </div>

                    {/* Transcript */}
                    <div ref={transcriptRef} className="flex-1 h-48 overflow-y-auto p-3 bg-gray-50 dark:bg-gray-900/50 text-xs space-y-2">
                        {transcript ? (
                            transcript.split("\n").map((line, i) => (
                                <div key={i} className={`p-2 rounded ${line.startsWith("User:") ? "bg-indigo-100 dark:bg-indigo-900/30 ml-8" : "bg-white dark:bg-gray-800 mr-8 border dark:border-gray-700"}`}>
                                    {line}
                                </div>
                            ))
                        ) : (
                            <div className="text-center text-gray-400 mt-4">Hi! Ask me to "Sign you up" or "Log in".</div>
                        )}
                    </div>

                    {/* Input Area */}
                    <div className="p-3 border-t dark:border-gray-700 bg-white dark:bg-gray-800 flex items-center gap-2">
                        <input
                            className="flex-1 bg-gray-100 dark:bg-gray-900 border-none rounded-full px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none dark:text-white"
                            placeholder="Type request..."
                            disabled={busy}
                            onKeyDown={async (e) => {
                                if (e.key === "Enter" && e.target.value.trim()) {
                                    const val = e.target.value;
                                    e.target.value = "";
                                    await sendTextToAgent(val);
                                }
                            }}
                        />
                        <button
                            className={`p-2 rounded-full ${listening ? "bg-red-500 animate-pulse" : "bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600"}`}
                            onClick={() => setListening(!listening)}
                            title="Microphone (Mock)"
                        >
                            Start
                        </button>
                    </div>
                </div>
            )}
        </>
    );
}
