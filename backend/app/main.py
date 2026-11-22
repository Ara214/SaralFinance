import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import config
from .ai_service import PROMPTS, AnalysisError, analyze
from .examples import EXAMPLES
from .risk_model import assess_message, load_classifier
from .schemas import AnalyzeRequest, CompareRequest


@asynccontextmanager
async def lifespan(_app):
    await asyncio.to_thread(load_classifier)
    yield

app = FastAPI(title="SaralFinance", version="1.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=config.ORIGINS, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])


@app.middleware("http")
async def no_cache(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(RequestValidationError)
async def invalid_input(_, error):
    return JSONResponse({"detail": "Check the message length and selected language.",
                         "fields": [item["loc"][-1] for item in error.errors()]}, status_code=422)


@app.exception_handler(AnalysisError)
async def analysis_failed(_, error):
    return JSONResponse({"detail": error.detail}, status_code=error.status)


@app.get("/health")
def health():
    return {"status": "ok", "mode": "gemini" if os.getenv("GEMINI_API_KEY") else "local"}


@app.get("/api/examples")
def examples():
    return EXAMPLES


@app.get("/api/prompts")
def prompts():
    return [{"id": version, "name": name, "description": description}
            for version, (name, description, _) in PROMPTS.items()]


@app.post("/api/analyze")
async def analyze_message(request: AnalyzeRequest):
    return await analyze(request.message, request.language, request.prompt_version or "P2",
                         allow_local=request.prompt_version is None)


@app.post("/api/compare")
async def compare(request: CompareRequest):
    risk = await asyncio.to_thread(assess_message, request.message, request.language)
    versions = list(PROMPTS)
    outcomes = await asyncio.gather(*(analyze(request.message, request.language, version, risk)
                                     for version in versions), return_exceptions=True)
    if all(isinstance(outcome, AnalysisError) for outcome in outcomes):
        raise outcomes[0]
    results = []
    for version, outcome in zip(versions, outcomes):
        if isinstance(outcome, AnalysisError):
            results.append({"prompt_version": version, "error": outcome.detail})
        elif isinstance(outcome, BaseException):
            raise outcome
        else:
            results.append(outcome)
    return {"results": results, "risk": risk}
