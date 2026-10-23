"""Pollinations / Flux image generation service for construction visualization."""

import os

from schemas.models import VisualizationRequest, VisualizationResponse

POLLINATIONS_BASE_URL = os.getenv(
    "POLLINATIONS_BASE_URL",
    "https://image.pollinations.ai/prompt",
)
DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 768


def generate_visualization(
    request: VisualizationRequest,
) -> VisualizationResponse:
    """Build a Pollinations.ai (Flux) image generation URL from a text prompt.

    The Pollinations image endpoint streams a generated image at the returned URL,
    so the response is fully synchronous and deterministic for a given prompt/seed.
    """
    clean_prompt = " ".join(request.prompt.split()).strip()
    image_url = (
        f"{POLLINATIONS_BASE_URL}/{clean_prompt}"
        f"?width={request.width}&height={request.height}"
        f"&model=flux&nologo=true"
    )
    return VisualizationResponse(
        image_url=image_url,
        prompt=clean_prompt,
    )
