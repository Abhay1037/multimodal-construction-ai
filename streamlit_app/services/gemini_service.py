"""Gemini (multimodal LLaMA-class LLM) service for construction safety, cracks and chat."""

import base64
import json
import os
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from google.generativeai import types

from utils import demo_responses

MODEL_NAME = "gemini-1.5-flash"

PPE_PROMPT = (
    "You are a senior construction safety officer specializing in PPE compliance under OSHA and "
    "IS 456 standards. Analyze this construction site photo. Respond with only a valid JSON object "
    "and no other text. The JSON must have exactly these keys: "
    '"safety_score" (integer 0-100), '
    '"overall_status" (one of "Compliant", "Needs Attention", "Critical"), '
    '"ppe_checklist" (array of objects with keys "item", "detected" (boolean), "required" (boolean)), '
    '"hazards" (array of objects with keys "hazard" (string), "severity" '
    '(one of "Low", "Medium", "High", "Critical"), "remedy" (string)).'
)

CRACK_PROMPT = (
    "You are a senior structural engineer specializing in concrete crack diagnostics. "
    "Analyze this construction photo. Respond with only a valid JSON object and no other text. "
    "The JSON must have exactly these keys: "
    '"defect_type" (one of "Hairline", "Settlement", "Structural Shear", "Thermal Expansion", "Spalling"), '
    '"crack_width_mm" (number), '
    '"root_causes" (array of strings), '
    '"recommended_repairs" (array of strings such as "epoxy injection", "structural re-grouting"), '
    '"urgency" (one of "Low", "Medium", "High", "Critical").'
)


def get_api_key() -> Optional[str]:
    """Resolve the Gemini API key from env vars or Streamlit secrets."""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or ""
    if not api_key:
        try:
            from streamlit import secrets

            api_key = secrets.get("GEMINI_API_KEY", "") or ""
        except Exception:
            api_key = ""
    return api_key or None


def is_gemini_configured() -> bool:
    """Return True when a Gemini API key is available."""
    return get_api_key() is not None


def _get_model():
    api_key = get_api_key()
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name=MODEL_NAME)


def _generate_json(
    model,
    *,
    image_bytes: bytes,
    mime_type: str,
    prompt: str,
) -> Dict[str, Any]:
    """Run a multimodal Gemini call constrained to JSON output."""
    image_part = {
        "inline_data": {
            "mime_type": mime_type,
            "data": base64.b64encode(image_bytes).decode("utf-8"),
        }
    }
    content = {
        "role": "user",
        "parts": [
            {"text": prompt},
            image_part,
        ],
    }
    response = model.generate_content(
        content,
        generation_config={"response_mime_type": "application/json", "temperature": 0.2},
    )
    text = response.text
    if not text:
        raise ValueError("Gemini returned an empty response.")
    return json.loads(text)


def generate_ppe_assessment(
    *,
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    filename: str = "site_photo.jpg",
) -> Dict[str, Any]:
    """Multimodal PPE safety compliance assessment with graceful demo fallback."""
    model = _get_model()
    if model is None:
        return dict(demo_responses.DEMO_SAFETY_RESULT)

    try:
        return _generate_json(
            model,
            image_bytes=image_bytes,
            mime_type=mime_type,
            prompt=(
                f"Construction site photo filename: {filename}. {PPE_PROMPT}"
            ),
        )
    except Exception:
        return dict(demo_responses.DEMO_SAFETY_RESULT)


def generate_crack_assessment(
    *,
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    filename: str = "concrete_wall.jpg",
) -> Dict[str, Any]:
    """Multimodal concrete crack / structural defect assessment with demo fallback."""
    model = _get_model()
    if model is None:
        return dict(demo_responses.DEMO_CRACK_RESULT)

    try:
        return _generate_json(
            model,
            image_bytes=image_bytes,
            mime_type=mime_type,
            prompt=f"Concrete wall photo filename: {filename}. {CRACK_PROMPT}",
        )
    except Exception:
        return dict(demo_responses.DEMO_CRACK_RESULT)


def create_chat():
    """Create a Gemini chat session, or None when unconfigured."""
    model = _get_model()
    if model is None:
        return None
    return model.start_chat()


def send_chat(chat, message: str) -> str:
    """Send a chat turn to the Gemini assistant with graceful demo fallback."""
    if chat is None:
        return demo_responses.demo_chat_response(message)
    try:
        response = chat.send_message(message)
        return response.text or demo_responses.demo_chat_response(message)
    except Exception:
        return demo_responses.demo_chat_response(message)
