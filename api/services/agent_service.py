from typing import Dict, Any, Optional
import os
import google.generativeai as genai
import json
import pyautogui
import time
import subprocess
from PIL import Image
from api.services.conversation_manager import conversation_manager

class AgentService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
            self.vision_model = genai.GenerativeModel('gemini-1.5-flash-latest')
    async def handle_conversation_state(self, session_id: str, state: Dict, text: str):
        intent = state.get("intent")
        step = state.get("step")

        if intent == "git_clone" and step == "ask_directory":
            target_dir = text.strip()
            conversation_manager.clear_state(session_id)
            return {
                "render": {
                    "type": "render",
                    "text": f"Understood. Cloning repository into {target_dir}.",
                    "tts": True,
                    "avatar_image_id": "male_business_portrait_v1"
                },
                "action": {
                    "type": "command",
                    "command": f"echo 'Cloning into {target_dir}'"
                }
            }
        return {"render": {"text": "I lost my train of thought. Let's start over."}}

    async def handle_visual_grounding(self, text: str):
        screenshot_path = "storage/temp_grounding.png"
        try:
            pyautogui.screenshot(screenshot_path)
            img = Image.open(screenshot_path)
            
            prompt = f"""
            Find the element on the screen matching the description: '{text}'.
            Return a JSON object with a single bounding box in [ymin, xmin, ymax, xmax] format (0-1000 scale) and the label.
            Format: {{ "box_2d": [ymin, xmin, ymax, xmax], "label": "found element" }}
            If not found, return empty JSON {{}}.
            Only return JSON.
            """
            
            response = self.vision_model.generate_content([prompt, img])
            print(f"Grounding Raw Response: {response.text}")
            
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                box = data.get("box_2d")
                
                if box:
                    screen_w, screen_h = pyautogui.size()
                    ymin, xmin, ymax, xmax = box
                    x = (xmin / 1000) * screen_w
                    y = (ymin / 1000) * screen_h
                    w = ((xmax - xmin) / 1000) * screen_w
                    h = ((ymax - ymin) / 1000) * screen_h
                    
                    highlights = [{
                        "x": int(x), "y": int(y), 
                        "width": int(w), "height": int(h), 
                        "label": text
                    }]
                    
                    return {
                        "render": {
                            "type": "render",
                            "text": f"I found it right here.",
                            "tts": True,
                            "highlights": highlights,
                            "avatar_image_id": "male_business_portrait_v1"
                        }
                    }
            return {"render": {"text": "I couldn't locate that on the screen.", "tts": True}}
        except Exception as e:
            print(f"Grounding Error: {e}")
            return {"render": {"text": "I had trouble seeing the screen.", "tts": True}}

    async def parse_intent(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        return await self._parse_intent_logic(text, context)

    async def _parse_intent_logic(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Parses user text into structured intent using Gemini (Mocked for now).
        """
        print(f"Agent received text: {text}")
        session_id = "default_session" # For now, single user
        text_lower = text.lower()
        
        # --- 0. CHECK ACTIVE CONVERSATION STATE ---
        state = conversation_manager.get_state(session_id)
        if state:
            return await self.handle_conversation_state(session_id, state, text)

        # -1. VISUAL GROUNDING (New Phase 26)
        grounding_keywords = ["where is", "show me", "highlight", "find the", "point to"]
        if any(x in text_lower for x in grounding_keywords):
            return await self.handle_visual_grounding(text)

        # -1. VISION ANALYSIS (New Phase 25)
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

        # --- 1. GIT CLONE INTENT (Multi-Turn) ---
        if "clone this repo" in text_lower or "clone repository" in text_lower:
             conversation_manager.set_intent(session_id, "git_clone", "ask_directory")
             return {
                 "render": {
                     "type": "ask",
                     "text": "Sure, I can clone this repository. Which directory should I clone it into?",
                     "tts": True,
                     "avatar_image_id": "male_business_portrait_v1",
                     "session_id": "generic_sure" # Reusing 'Sure, I can do that' + custom text? 
                     # Wait, if text differs, TTS differs. Session ID collision!
                     # If I set session_id to "generic_which_dir", text MUST match PREDEFINED_RESPONSES.
                 }
             }

        if "clone this repo" in text_lower or "clone repository" in text_lower:
             import re
             import shutil
             
             # Helper to get clipboard
             def get_clipboard():
                 try:
                     # Use PowerShell to get clipboard content
                     res = subprocess.run(["powershell", "-command", "Get-Clipboard"], capture_output=True, text=True)
                     return res.stdout.strip()
                 except:
                     return ""

             # 1. Parse Directory
             dir_match = re.search(r"(?:in|into|to)\s+(not the\s+)?(my\s+)?([\w\s]+)", text_lower)
             target_dir_name = "cloned_repo"
             
             if dir_match:
                 raw_dir = dir_match.group(3).strip().lower()
                 raw_dir = raw_dir.replace("folder", "").replace("directory", "").strip()
                 target_dir_name = raw_dir
             
             # 2. Resolve Path
             home = os.path.expanduser("~")
             if "download" in target_dir_name:
                 base_path = os.path.join(home, "Downloads")
             elif "document" in target_dir_name:
                 base_path = os.path.join(home, "Documents")
             elif "desktop" in target_dir_name:
                 base_path = os.path.join(home, "Desktop")
             else:
                 base_path = os.path.join(home, "Downloads") # Default to Downloads
             
             print(f"DEBUG: Clone Target: {target_dir_name} -> {base_path}")

             # 3. Get URL (Try to grab from browser)
             # Focus Address Bar -> Copy
             try:
                 # Attempt to switch back to browser (Alt+Tab) just in case overlay stole focus
                 print("DEBUG: Switching focus (Alt+Tab)...")
                 pyautogui.hotkey('alt', 'tab')
                 time.sleep(0.5) 
                 
                 pyautogui.hotkey('ctrl', 'l')
                 time.sleep(0.2)
                 pyautogui.hotkey('ctrl', 'c')
                 time.sleep(0.2)
                 repo_url = get_clipboard()
                 print(f"DEBUG: Clipboard URL: '{repo_url}'")
                 
                 # Basic validation
                 if not repo_url or "http" not in repo_url:
                     raise ValueError("Clipboard does not contain a valid URL")
                     
                 # Extract repo name for folder if generic target
                 if target_dir_name == "cloned_repo":
                     repo_name = repo_url.split("/")[-1].replace(".git", "")
                     final_path = os.path.join(base_path, repo_name)
                 else:
                     final_path = os.path.join(base_path, target_dir_name)

                 # 4. Execute Clone
                 # Run in background so we don't block
                 cmd = f'git clone {repo_url} "{final_path}"'
                 print(f"DEBUG: Executing: {cmd}")
                 subprocess.Popen(cmd, shell=True)
                 
                 return {
                    "render": {
                        "type": "render",
                        "text": f"Cloning {repo_url} into {final_path}.",
                        "tts": True,
                        "avatar_image_id": "male_business_portrait_v1",
                        "session_id": "generic_sure"
                    },
                    "action": None # Handled on backend
                }
             except Exception as e:
                 print(f"Clone Error: {e}")
                 return {
                     "render": {
                         "type": "render",
                         "text": "I couldn't get the URL or run the command. Make sure you are on a GitHub page.",
                         "tts": True
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
             import webbrowser

             if browser_cmd and url:
                 target_url = url if url.startswith("http") else f"https://{url}"
                 # Specific browser launch
                 subprocess.Popen(f'start {browser_cmd} "{target_url}"', shell=True)
                 response_text = f"Opening {browser_cmd.capitalize()} to {url}."
                 
             elif url and "go to" in text_lower:
                 # "Go to youtube.com" (Default Browser)
                 target_url = url if url.startswith("http") else f"https://{url}"
                 webbrowser.open(target_url) 
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
                "render": {"type": "render", "text": "Logging you out.", "tts": True, "session_id": "generic_done"},
                "action": {"type": "action", "action_type": "click", "target": ".logout", "target_name": "Logout Button"}
            }

        # 4. General Navigation
        if "home" in text_lower or "main page" in text_lower:
             return {
                "render": {"type": "render", "text": "Going Home.", "tts": True, "session_id": "navigation_going_home"},
                "action": {"type": "action", "action_type": "navigate", "payload": {"route": "/"}}
            }
        if "about us" in text_lower or "about company" in text_lower:  # Restricted
             return {
                "render": {"type": "render", "text": "Showing About Us.", "tts": True, "session_id": "generic_opening"},
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
                    "session_id": "auth_login"
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
                    "session_id": "generic_listening" # or 'greeting_v1' if we want custom
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
                "avatar_image_id": "male_business_portrait_v1",
                "session_id": "generic_thinking"
            },
            "action": None
        }
