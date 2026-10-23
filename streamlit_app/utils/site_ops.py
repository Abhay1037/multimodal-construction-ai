"""Weather advisories and demo-mode assistant responses for the site operations tab."""

WEATHER_CONDITIONS = {
    "Normal": {
        "severity": "Low",
        "title": "Normal Site Conditions",
        "advisory": (
            "All operations may proceed as scheduled. Continue routine concrete curing "
            "monitoring, inspection cadence and toolbox talks."
        ),
        "affected_activity": "General site operations",
    },
    "High Wind": {
        "severity": "High",
        "title": "High Wind Advisory",
        "advisory": (
            "Suspend crane operations and material lifts. Secure loose scaffolding and "
            "tie-downs. Implement wind-speed monitoring and ground crew traffic control."
        ),
        "affected_activity": "Crane & lifting operations",
    },
    "Heavy Rain": {
        "severity": "Critical",
        "title": "Heavy Rain Protocol",
        "advisory": (
            "Suspend excavation and concrete pouring. Protect electrical equipment from "
            "water ingress and implement dewatering where needed."
        ),
        "affected_activity": "Excavation / concrete works / electrical safety",
    },
    "Extreme Heat": {
        "severity": "High",
        "title": "Extreme Heat Advisory",
        "advisory": (
            "Enforce heat-illness prevention: hydration plans, shade, PPE; delay or slow "
            "concrete pour and use curing protocols for heat of hydration."
        ),
        "affected_activity": "All outdoor work / concrete curing",
    },
}


def get_weather_alerts(condition: str) -> dict:
    """Return the safety alert associated with a weather condition."""
    return WEATHER_CONDITIONS.get(condition, WEATHER_CONDITIONS["Normal"])


def demo_chat_response(message: str) -> str:
    """Graceful keyword-based assistant response used when no LLM API key is set."""
    text = (message or "").lower()

    if any(word in text for word in ("safety", "ppe", "helmet", "harness", "vest", "boot", "harassment")):
        return (
            "Based on OSHA and IS 456 practices: conduct daily toolbox talks, enforce PPE "
            "visibility for all workers, and verify safety harness anchor points before any "
            "elevated work. Stop work immediately if a hazard is observed."
        )
    if any(word in text for word in ("crack", "structural", "settle", "spall", "defect", "shear", "thermal", "expansion")):
        return (
            "For structural cracks: verify crack width and orientation, isolate affected zone, "
            "and engage a structural engineer. Non-structural cracks may use epoxy injection; "
            "shear/settlement cracks typically require structural re-grouting or underpinning."
        )
    if any(word in text for word in ("cost", "budget", "valuation", "price", "estimate", "market", "roi")):
        return (
            "Use the Planning & Real Estate Valuation tab: enter structure type, built-up area, "
            "location tier and completion % to compute budget, CAPEX, market valuation and "
            "steel/cement requirements in INR."
        )
    if any(word in text for word in ("weather", "rain", "wind", "heat", "storm", "thunder", "temperature")):
        return (
            "Consult the Daily Site Assistant: during High Wind crane ops are suspended, Heavy "
            "Rain pauses concrete works, and Extreme Heat requires hydration and curing protocols."
        )
    if any(word in text for word in ("plan", "milestone", "schedule", "timeline", "progress", "estimate")):
        return (
            "The construction plan milestone engine tracks progress through Planning & Real Estate "
            "Valuation using weighted phase milestones and completion percentage."
        )
    return (
        "I am the construction engineering assistant. I can help with site safety (PPE), crack "
        "diagnostics, cost planning, valuation, weather advisories and project milestones. "
        "Please ask a construction-related question."
    )
