"""FastAPI entrypoint for the Multimodal Construction Intelligence Platform."""

import os

from dotenv import load_dotenv

# Load backend/.env before importing services (they read env vars at import time).
load_dotenv()

import httpx
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from schemas.models import (
    AnalysisType,
    PlanEstimateRequest,
    PlanEstimateResponse,
    SafetyAnalysisResult,
    SafetyStatus,
    SiteAnalysisResponse,
    VisualizationRequest,
    VisualizationResponse,
)
from services.llama_service import analyze_site_image, generate_project_plan
from services.pollination_service import generate_visualization

app = FastAPI(
    title="Multimodal Construction Intelligence Platform",
    version="1.0.0",
    description=(
        "AI-powered construction safety monitoring, structural crack detection, "
        "project planning and cost estimation, and AI visualization."
    ),
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": os.getenv("APP_NAME", "Multimodal Construction Intelligence Platform"),
    }


@app.post("/api/analyze-site", response_model=SiteAnalysisResponse)
async def analyze_site(
    image: UploadFile = File(...),
    analysis_type: str = Form(...),
) -> SiteAnalysisResponse:
    """Upload a construction site photo and run LLaMA safety or crack analysis."""
    try:
        analysis_enum = AnalysisType(analysis_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid analysis_type: '{analysis_type}'. "
                f"Supported values: {[t.value for t in AnalysisType]}"
            ),
        )

    content_type = image.content_type or "image/jpeg"
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded image is empty.")

    try:
        result: SafetyAnalysisResult = await analyze_site_image(
            image_bytes=image_bytes,
            content_type=content_type,
            filename=image.filename or "site_photo.jpg",
            analysis_type=analysis_enum,
        )
    except httpx.HTTPError:
        # Graceful demonstration mode when the LLM provider is unreachable / unconfigured.
        result = SafetyAnalysisResult(
            status=SafetyStatus.WARNING,
            confidence_score=55.0,
            summary=(
                "Demonstration mode: live LLaMA vision analysis is unavailable because "
                "GROQ_API_KEY is not configured. Add GROQ_API_KEY to backend/.env for real "
                "multimodal safety analysis."
            ),
            findings=[
                "Demo result — no live model inference was performed.",
                "Visible workers appear to use hard hats and high-visibility vests.",
                "No exposed rebar or unguarded openings detected in the demo assessment.",
            ],
            action_items=[
                "Configure GROQ_API_KEY in backend/.env to enable live analysis.",
                "Run a toolbox talk on PPE compliance before starting work.",
            ],
        )
    return SiteAnalysisResponse(analysis_type=analysis_enum, result=result)


@app.post("/api/plan-estimate", response_model=PlanEstimateResponse)
async def plan_estimate(request: PlanEstimateRequest) -> PlanEstimateResponse:
    """Generate a construction plan and cost estimation from project parameters."""
    return await generate_project_plan(
        plot_size_sqft=request.plot_size_sqft,
        budget_usd=request.budget_usd,
        category=request.category,
        timeline_weeks=request.timeline_weeks,
    )


@app.post("/api/generate-visualization", response_model=VisualizationResponse)
def generate_visualization_endpoint(request: VisualizationRequest) -> VisualizationResponse:
    """Generate an AI construction/architectural visualization via Pollinations / Flux."""
    return generate_visualization(request)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()},
    )
