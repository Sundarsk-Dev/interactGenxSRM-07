from typing import Dict, Any, Optional
import uuid

class ConversationManager:
    """
    Manages multi-turn conversation state.
    In-memory storage for simplicity (can be upgraded to Redis/DB).
    """
    def __init__(self):
        # Maps session_id (or user_id) -> State Dict
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def get_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._sessions.get(session_id)

    def update_state(self, session_id: str, new_state: Dict[str, Any]):
        if session_id not in self._sessions:
            self._sessions[session_id] = {}
        self._sessions[session_id].update(new_state)

    def clear_state(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]

    def set_intent(self, session_id: str, intent: str, step: str = "start", data: Dict = None):
        self._sessions[session_id] = {
            "intent": intent,
            "step": step,
            "data": data or {}
        }

# Global Instance
conversation_manager = ConversationManager()
