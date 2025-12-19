# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import speech, questions
from pathlib import Path

app = FastAPI(
    title="TOEFL Speaking AI Consultant",
    description="AI-powered TOEFL Speaking evaluation service",
    version="1.0.0"
)

# CORS middleware configuration - MUST be added BEFORE mounting static files
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow all Vercel subdomains
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:5174",
        "https://eda-cap.vercel.app",  # Production Vercel frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Important for audio files
)

# Static files for audio
static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Mount data directory for audio files
data_path = Path(__file__).parent / "data"
if data_path.exists():
    app.mount("/data", StaticFiles(directory=str(data_path)), name="data")

# Include routers
app.include_router(speech.router)
app.include_router(questions.router)

@app.get("/")
async def root():
    return {
        "message": "TOEFL Speaking AI Consultant API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/debug/audio-files")
async def debug_audio_files():
    """Debug endpoint to check if audio files exist"""
    import os
    data_path = Path(__file__).parent / "data" / "q2_listening"
    files = []
    if data_path.exists():
        files = [f.name for f in data_path.glob("*.mp3")]
    return {
        "data_path_exists": data_path.exists(),
        "data_path": str(data_path),
        "mp3_files": files,
        "file_count": len(files)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
