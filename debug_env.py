import sys
import os

print(f"Executable: {sys.executable}")
print("Sys Path:")
for p in sys.path:
    print(f"  - {p}")

try:
    import fastapi
    print(f"FastAPI found at: {fastapi.__file__}")
except ImportError as e:
    print(f"FastAPI not found: {e}")

try:
    import uvicorn
    print(f"Uvicorn found at: {uvicorn.__file__}")
except ImportError as e:
    print(f"Uvicorn not found: {e}")
