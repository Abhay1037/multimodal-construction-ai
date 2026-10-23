"""LLaMA service for multimodal site safety/structural analysis and planning."""

import base64
import json
import os
import re
from typing import Any, Dict, List

import httpx

from schemas.models import (
    AnalysisType,
    ConstructionCategory,
    Milestone,
    PlanEstimateResponse,
    SafetyAnalysisResult,
    SafetyStatus,
)

GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_LLAMA_MODEL = os.getenv("LLAMA_MODEL", "llama-3.2-11b-vision-preview")
TIMEOUT_SECONDS = float(os.getenv("LLAMA_TIMEOUT_SECONDS", "30"))

SYSTEM_PROMPTS: Dict[AnalysisType, str] = {
    AnalysisType.SAFETY_MONITORING: (
        "You are an expert construction safety officer with deep knowledge of PPE usage, "
        "site hazard identification and safety regulations. Analyze the provided construction "
        "site photo. You must respond with ONLY a single valid JSON object and no additional text. "
        "The JSON object must have exactly these keys: "
        '"status" (one of: "Safe", "Warning", "Hazardous"), '
        '"confidence_score" (a number between 0 and 100), '
        '"summary" (a short narrative of the observed conditions), '
        '"findings" (an array of specific observed safety issues), '
        '"action_items" (an array of recommended corrective actions).'
    ),
    AnalysisType.CRACK_DETECTION: (
        "You are a senior structural engineer specializing in crack and deformation detection "
        "in concrete construction. Analyze the provided construction photo. You must respond with "
        "ONLY a single valid JSON object and no additional text. The JSON object must have exactly "
        "these keys: "
        '"status" (one of: "Safe", "Warning", "Hazardous"), '
        '"confidence_score" (a number between 0 and 100), '
        '"summary" (a short narrative of the observed structural conditions), '
        '"findings" (an array of specific crack observations with severity), '
        '"action_items" (an array of recommended inspection and mitigation steps).'
    ),
}

PLAN_SYSTEM_PROMPT = (
    "You are a veteran construction project manager and cost estimator. "
    "Generate a construction project plan as a single valid JSON object. "
    "The JSON object must have exactly these keys: "
    '"estimated_cost_usd" (total estimated construction cost in USD as a number), '
    '"feasibility" (one of: "Feasible", "Borderline", "Infeasible"), '
    '"milestones" (an array of objects with keys: "week" (integer), "milestone" (string), '
    '"tasks" (array of strings describing the work for that week)).'
)


async def _invoke_llama(
    client: httpx.AsyncClient,
    *,
    system_prompt: str,
    messages: list,
    model: str,
) -> str:
    response = await client.post(
        GROQ_CHAT_COMPLETIONS_URL,
        headers={
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY', '')}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "temperature": 0.2,
            "max_tokens": 1500,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": messages},
            ],
        },
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["choices"][0]["message"]["content"]


def _extract_json(text: str) -> Dict[str, Any]:
    """Strip markdown code fences and parse the first JSON object found."""
    cleaned = re.sub(r"```(?:json)?", "", text or "").strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start : end + 1]
    return json.loads(cleaned)


def _to_data_url(content_type: str, image_bytes: bytes) -> str:
    media_type = content_type if content_type and content_type.startswith("image/") else "image/jpeg"
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{media_type};base64,{encoded}"


def _heuristic_plan(
    *,
    plot_size_sqft: float,
    budget_usd: float,
    category: ConstructionCategory,
    timeline_weeks: int,
) -> PlanEstimateResponse:
    """Fallback construction plan used when the LLM provider is unavailable."""
    cost_per_sqft = 145.0 if category == ConstructionCategory.RESIDENTIAL else 295.0
    estimated_cost_usd = round(plot_size_sqft * cost_per_sqft, 2)
    feasibility = "Feasible" if budget_usd >= estimated_cost_usd * 0.9 else "Infeasible"

    milestone_specs = [
        (2, "Design & Approvals", ["Finalize architectural drawings", "Submit permits"]),
        (6, "Foundation & Framing", ["Site clearing", "Excavation & footings", "Structural framing"]),
        (12, "Envelope & MEP Rough-in", ["Roofing & waterproofing", "Exterior cladding", "MEP rough-in"]),
        (20, "Finishes & Commissioning", ["Interior finishes", "MEP final install", "Inspections & handover"]),
    ]
    milestones = [
        Milestone(week=week, milestone=milestone, tasks=tasks)
        for week, milestone, tasks in milestone_specs
        if week <= timeline_weeks
    ]
    return PlanEstimateResponse(
        category=category,
        plot_size_sqft=plot_size_sqft,
        budget_usd=budget_usd,
        timeline_weeks=timeline_weeks,
        estimated_cost_usd=estimated_cost_usd,
        estimated_cost_per_sqft=cost_per_sqft,
        feasibility=feasibility,
        milestones=milestones,
    )


async def analyze_site_image(
    *,
    image_bytes: bytes,
    content_type: str,
    filename: str,
    analysis_type: AnalysisType,
) -> SafetyAnalysisResult:
    """Run LLaMA multimodal vision analysis on a construction site photo."""
    model = os.getenv("LLAMA_MODEL", DEFAULT_LLAMA_MODEL)
    image_url = _to_data_url(content_type, image_bytes)

    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        content = await _invoke_llama(
            client,
            system_prompt=SYSTEM_PROMPTS[analysis_type],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Construction site photo: {filename}. Perform {analysis_type.value} analysis.",
                        },
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            model=model,
        )

    payload = _extract_json(content)
    status_raw = str(payload.get("status") or "Warning")
    status = next((s for s in SafetyStatus if s.value.lower() == status_raw.lower()), SafetyStatus.WARNING)

    confidence = float(payload.get("confidence_score") or 50.0)
    findings: List[str] = [str(f) for f in (payload.get("findings") or [])]
    action_items: List[str] = [str(a) for a in (payload.get("action_items") or [])]

    return SafetyAnalysisResult(
        status=status,
        confidence_score=min(max(confidence, 0.0), 100.0),
        summary=str(payload.get("summary") or "The model did not produce a narrative summary."),
        findings=findings,
        action_items=action_items,
    )


async def generate_project_plan(
    *,
    plot_size_sqft: float,
    budget_usd: float,
    category: ConstructionCategory,
    timeline_weeks: int,
) -> PlanEstimateResponse:
    """Generate a structured construction plan with cost estimation via LLaMA."""
    model = os.getenv("LLAMA_MODEL", DEFAULT_LLAMA_MODEL)

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            content = await _invoke_llama(
                client,
                system_prompt=PLAN_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Generate a construction project plan for: plot size {plot_size_sqft} sq ft, "
                            f"budget ${budget_usd}, category {category.value}, timeline {timeline_weeks} weeks."
                        ),
                    }
                ],
                model=model,
            )

        payload = _extract_json(content)
        estimated_cost_usd = float(payload.get("estimated_cost_usd") or 0.0)
        if estimated_cost_usd <= 0:
            raise ValueError("Missing estimated_cost_usd")
        feasibility = str(payload.get("feasibility") or "Borderline")

        milestones: List[Milestone] = []
        for index, item in enumerate(payload.get("milestones") or []):
            milestones.append(
                Milestone(
                    week=int(item.get("week") or index + 1),
                    milestone=str(item.get("milestone") or f"Phase {index + 1}"),
                    tasks=[str(t) for t in (item.get("tasks") or [])],
                )
            )
    except (httpx.HTTPError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        return _heuristic_plan(
            plot_size_sqft=plot_size_sqft,
            budget_usd=budget_usd,
            category=category,
            timeline_weeks=timeline_weeks,
        )

    cost_per_sqft = round(estimated_cost_usd / plot_size_sqft, 2) if plot_size_sqft else 0.0
    return PlanEstimateResponse(
        category=category,
        plot_size_sqft=plot_size_sqft,
        budget_usd=budget_usd,
        timeline_weeks=timeline_weeks,
        estimated_cost_usd=estimated_cost_usd,
        estimated_cost_per_sqft=cost_per_sqft,
        feasibility=feasibility,
        milestones=milestones,
    )
