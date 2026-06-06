from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routes import grading, rubric, submissions

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Vietnamese Literature Grading Backend",
    description="Draft grading backend for K-12 Vietnamese literature essays.",
    version="0.1.0",
)

app.include_router(rubric.router)
app.include_router(grading.router)
app.include_router(submissions.router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "message": "Grading backend is running",
    }


@app.get("/ui", include_in_schema=False)
def grading_ui() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
