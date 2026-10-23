"""Pollinations / Flux image generation service for construction visualization."""

import requests
from urllib.parse import quote

POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt"
DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 768


def build_visualization_prompt(
    structure_type: str,
    built_up_sqft: float,
    location_label: str,
) -> str:
    """Build an architectural concept prompt for the 3D visualization model."""
    return (
        f"{structure_type} construction project, {built_up_sqft:.0f} sq ft built-up area, "
        f"{location_label}, photorealistic 3D architectural rendering, modern construction site"
    )


def build_image_url(prompt: str, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT) -> str:
    """Build a Pollinations / Flux image generation URL for the prompt."""
    return (
        f"{POLLINATIONS_BASE_URL}/{quote(prompt)}?width={width}&height={height}"
        f"&model=flux&nologo=true"
    )


def get_image_bytes(image_url: str, timeout: int = 60) -> bytes:
    """Fetch the generated architectural image bytes from the Pollinations endpoint."""
    response = requests.get(image_url, timeout=timeout)
    response.raise_for_status()
    return response.content
