from typing import Dict, Any, Optional
import os
import google.generativeai as genai
import json
import pyautogui
import time
import subprocess
from PIL import Image

class AgentService:
    def __init__(self):
        # In a real scenario, we would initialize Gemini here
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
            self.vision_model = genai.GenerativeModel('gemini-1.5-flash-latest') # Use latest alias
            
    async def parse_intent(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Parses user text into structured intent using Gemini (Mocked for now).
        """
        print(f"Agent received text: {text}")
        
        # --- MOCK LOGIC (Rule-based Fallback) ---
        text_lower = text.lower()
        
        # -1. VISION ANALYSIS (New Phase 25)
        # Catch "tell me about...", "describe...", "what is..."
        vision_keywords = [
            "info about", "about this page", "about this website", 
            "what is on", "summary of", "describe this", 
            "what is going on", "tell me about it", "look at this"
        ]
        
        if any(x in text_lower for x in vision_keywords):
             screenshot_path = "storage/temp_vision.png"
             try:
                 # 1. Capture Screen
                 pyautogui.screenshot(screenshot_path)
                 
                 # 2. Analyze with Gemini Vision
                 img = Image.open(screenshot_path)
                 response = self.vision_model.generate_content(["Describe this webpage in detail for a blind user. Focus on the main content and key actions available. Keep it under 50 words.", img])
                 description = response.text
             except Exception as e:
                 import traceback
                 traceback.print_exc()
                 print(f"Vision Error: {e}")
                 description = f"I'm sorry, I couldn't analyze the screen. Error: {str(e)[:50]}"
                 
             return {
                 "render": {
                     "type": "render",
                     "text": description,
                     "tts": True,
                     "voice": "en-US-ChristopherNeural",
                     "avatar_image_id": "male_business_portrait_v1",
                     "session_id": f"vision_{int(time.time())}"
                 }
             }

        # 0. DESKTOP AUTOMATION (Enhancement Phase)
        if "open" in text_lower or "start" in text_lower or "go to" in text_lower:
             import re
             
             # Clean input
             cmd = text_lower.replace("open ", "").replace("start ", "").replace("go to ", "").strip()
             
             # URL Detection Regex
             # Fixed: Escaped hyphen or placed at end to avoid range error
             url_match = re.search(r'(https?://)?(www\.)?[\w-]+\.[a-z]{2,}(/[\w\-./?%&=]*)?', text_lower)
             url = url_match.group(0) if url_match else None
             
             # App Detection
             is_chrome = "chrome" in text_lower or "browser" in text_lower
             is_brave = "brave" in text_lower
             is_edge = "edge" in text_lower
             is_notepad = "notepad" in text_lower
             is_calc = "calculator" in text_lower
             is_vscode = "vs code" in text_lower or "code" in text_lower
             is_spotify = "spotify" in text_lower
             
             response_text = ""

             # Browser Logic (Chrome, Brave, Edge)
             browser_cmd = "chrome" if is_chrome else "brave" if is_brave else "msedge" if is_edge else None
             
             if browser_cmd and url:
                 target_url = url if url.startswith("http") else f"https://{url}"
                 subprocess.Popen(f'start {browser_cmd} "{target_url}"', shell=True)
                 response_text = f"Opening {browser_cmd.capitalize()} to {url}."
                 
             elif url and "go to" in text_lower:
                 # "Go to youtube.com" (Default Browser)
                 target_url = url if url.startswith("http") else f"https://{url}"
                 subprocess.Popen(f'start "{target_url}"', shell=True)
                 response_text = f"Navigating to {url}."
                 
             elif browser_cmd:
                 subprocess.Popen(f"start {browser_cmd}", shell=True)
                 response_text = f"Opening {browser_cmd.capitalize()}."
                 
             elif is_notepad:
                 subprocess.Popen("notepad.exe")
                 response_text = "Opening Notepad."
                 
             elif is_calc:
                 subprocess.Popen("calc.exe")
                 response_text = "Opening Calculator."
                 
             elif is_vscode:
                 subprocess.Popen("code", shell=True)
                 response_text = "Opening VS Code."
                 
             elif is_spotify:
                 subprocess.Popen("start spotify", shell=True)
                 response_text = "Opening Spotify."
                 
             else:
                 # Generic Fallback (Type Search)
                 app_name = cmd.split(" and ")[0] # Handle "open X and Y" roughly
                 try:
                     pyautogui.press('win')
                     time.sleep(0.5)
                     pyautogui.write(app_name)
                     time.sleep(0.5)
                     pyautogui.press('enter')
                     response_text = f"Searching for {app_name}."
                 except Exception as e:
                     response_text = "I couldn't execute that command."

             return {
                 "render": {
                     "type": "render",
                     "text": response_text,
                     "tts": True,
                     "voice": "en-US-ChristopherNeural",
                     "avatar_image_id": "male_business_portrait_v1",
                     "session_id": f"desktop_cmd_{int(time.time())}"
                 }
             }
             
        # 1. Signup Flow (Chain: Open Modal -> Switch to Signup)
        if "sign up" in text_lower or "create account" in text_lower or "sign me up" in text_lower:
            return {
                "render": {
                    "type": "render",
                    "text": "Opening the registration form for you.",
                    "tts": True,
                    "voice": "en-US-ChristopherNeural",
                    "avatar_image_id": "male_business_portrait_v1",
                    "session_id": "signup_v1"
                },
                "action": {
                    "type": "action",
                    "action_type": "chain",
                    "actions": [
                        {
                            "action_type": "ensure_open",
                            "target": "body",
                            "class_name": "show-popup",
                            "target_name": "Login Modal"
                        },
                        {
                            "action_type": "click",
                            "target": "#signup-link",
                            "target_name": "Switch to Signup"
                        }
                    ]
                }
            }

        # 1b. Form Filling Intent (Username/Password)
        if "username is" in text_lower or "password is" in text_lower:
            payload = {}
            import re
            
            # Extract username
            u_match = re.search(r"username is (\w+)", text_lower)
            if u_match:
                payload["username"] = u_match.group(1)
                
            # Extract password (simple regex)
            p_match = re.search(r"password is (\S+)", text_lower)
            if p_match:
                payload["password"] = p_match.group(1)

            if payload:
                return {
                    "render": {
                        "type": "render",
                        "text": f"Filling the form with: {', '.join(payload.keys())}",
                        "tts": True,
                        "voice": "en-US-ChristopherNeural", 
                        "avatar_image_id": "male_business_portrait_v1"
                    },
                    "action": {
                        "type": "action",
                        "action_type": "fill_form",
                        "payload": payload,
                        "confirm_message": f"Fill form with {payload}?"
                    }
                }
            
        # 2. Join Exam Flow
        if "join exam" in text_lower or "take exam" in text_lower or "start exam" in text_lower:
            return {
                "render": {
                    "type": "render",
                    "text": "Navigating to the Exam Interface.",
                    "tts": True,
                    "voice": "en-US-ChristopherNeural",
                    "avatar_image_id": "male_business_portrait_v1",
                    "session_id": "join_exam_v1"
                },
                "action": {
                    "type": "action",
                    "action_type": "navigate",
                    "payload": { "route": "/monitoring/" },
                    "confirmation_required": False
                }
            }
            
        # 3. Dashboard Flow (and Sub-navigation)
        if "dashboard" in text_lower:
             # Just go to main dashboard view
             return {
                "render": {
                    "type": "render",
                    "text": "Taking you to your Dashboard.",
                    "tts": True,
                    "voice": "en-US-ChristopherNeural",
                    "avatar_image_id": "male_business_portrait_v1",
                    "session_id": "dashboard_v1"
                },
                "action": {
                    "type": "action",
                    "action_type": "chain",
                    "actions": [
                         # Ensure we are on the page first, then click (optional, but good for robustness)
                         {"action_type": "navigate", "payload": {"route": "/users/"}},
                         {"action_type": "click", "target": "#dashboard-link", "target_name": "Dashboard Tab"}
                    ]
                }
            }
            
        if any(x in text_lower for x in ["create exam", "create an exam", "create a test", "create new exam", "new room", "create test", "make an exam"]):
             is_dashboard = "/users/" in context.get("current_page", "")
             
             if is_dashboard:
                 action = {"type": "action", "action_type": "click", "target": "#create-exam-room-link", "target_name": "Create Exam Tab"}
             else:
                 action = {"type": "action", "action_type": "navigate", "payload": {"route": "/users/?agent_click=create-exam-room-link"}}
             
             return {
                "render": {"type": "render", "text": "Opening Create Exam Room section.", "tts": True},
                "action": action
            }
            
        if "manage student" in text_lower or "students" in text_lower:
             is_dashboard = "/users/" in context.get("current_page", "")
             if is_dashboard:
                 action = {"type": "action", "action_type": "click", "target": "#manage-student-link", "target_name": "Manage Students Tab"}
             else:
                 action = {"type": "action", "action_type": "navigate", "payload": {"route": "/users/?agent_click=manage-student-link"}}
                 
             return {
                "render": {"type": "render", "text": "Showing Manage Students section.", "tts": True},
                "action": action
            }
            
        if "logs" in text_lower or "report" in text_lower:
             is_dashboard = "/users/" in context.get("current_page", "")
             
             if is_dashboard:
                 action = {"type": "action", "action_type": "click", "target": "#log-reports-link", "target_name": "Logs Tab"}
             else:
                 action = {"type": "action", "action_type": "navigate", "payload": {"route": "/users/?agent_click=log-reports-link"}}
                 
             return {
                "render": {"type": "render", "text": "Opening Logs and Reports.", "tts": True},
                "action": action
            }
            
        if "logout" in text_lower or "sign out" in text_lower:
             return {
                "render": {"type": "render", "text": "Logging you out.", "tts": True, "session_id": "logout_v1"},
                "action": {"type": "action", "action_type": "click", "target": ".logout", "target_name": "Logout Button"}
            }

        # 4. General Navigation
        if "home" in text_lower or "main page" in text_lower:
             return {
                "render": {"type": "render", "text": "Going Home.", "tts": True, "session_id": "home_v1"},
                "action": {"type": "action", "action_type": "navigate", "payload": {"route": "/"}}
            }
        if "about us" in text_lower or "about company" in text_lower:  # Restricted
             return {
                "render": {"type": "render", "text": "Showing About Us.", "tts": True, "session_id": "about_v1"},
                "action": {"type": "action", "action_type": "navigate", "payload": {"route": "/#about"}}
            }

        # 5. Login Flow
        if "log in" in text_lower or "login" in text_lower:
            return {
                "render": {
                    "type": "render",
                    "text": "Okay, opening the login screen.",
                    "tts": True,
                    "avatar_image_id": "male_business_portrait_v1",
                    "session_id": "login_v1"
                },
                "action": {
                    "type": "action",
                    "action_type": "click",
                    "target": ".login-btn",
                    "target_name": "Login Button",
                    "confirmation_required": False
                }
            }
            
        # 3. Stop Flow
        if "stop" in text_lower:
             return {
                "render": {
                    "type": "render",
                    "text": "Stops speaking.",
                    "stop_playback": True
                }
            }

        # 4. Greeting Flow
        if any(x in text_lower for x in ["hello", "hi", "hey"]):
            return {
                "render": {
                    "type": "render",
                    "text": "Hi, how can I help you today?",
                    "tts": True,
                    "avatar_image_id": "male_business_portrait_v1",
                    "session_id": "greeting_v1"
                }
            }

        # 5. Default / Clarify (Context Aware)
        current_page = context.get("current_page", "") if context else ""
        
        fallback_text = "I'm not sure I understood. Do you want to sign up or log in?"
        
        if "/users/" in current_page:
            fallback_text = "I didn't quite catch that. You can ask me to create an exam, manage students, or show logs."
        elif "/monitoring/" in current_page:
             fallback_text = "We are in the Exam Area. Please say 'Join Exam' if you want to proceed."
             
        return {
            "render": {
                "type": "render",
                "text": fallback_text,
                "tts": True,
                "avatar_image_id": "male_business_portrait_v1"
            },
            "action": None
        }
