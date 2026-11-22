"""Serve the Vite build and API from the same origin."""
from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .main import app

dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
index = dist / "index.html"
app.mount("/assets", StaticFiles(directory=dist / "assets"), name="frontend-assets")


@app.get("/", include_in_schema=False)
@app.get("/analyze", include_in_schema=False)
@app.get("/how-it-works", include_in_schema=False)
@app.get("/about", include_in_schema=False)
def frontend():
    return FileResponse(index)
