"""
🌾 AGRIWISE AI - Launcher Script
Runs the FastAPI application on http://127.0.0.1:8000 using Uvicorn.
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import uvicorn

if __name__ == "__main__":
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
    sys.path.insert(0, backend_dir)

    app_dir = backend_dir
    print("🌾 Starting AGRIWISE AI Platform on http://127.0.0.1:8000 ...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, reload_dirs=[backend_dir])
