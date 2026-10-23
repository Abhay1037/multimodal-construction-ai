"""Fallback demonstration-mode analysis results for the Multimodal Construction Intelligence Platform."""

DEMO_SAFETY_RESULT = {
    "safety_score": 64,
    "overall_status": "Needs Attention",
    "ppe_checklist": [
        {"item": "Hard hat", "detected": True, "required": True},
        {"item": "High-visibility vest", "detected": True, "required": True},
        {"item": "Safety harness", "detected": False, "required": True},
        {"item": "Steel-toe boots", "detected": True, "required": True},
        {"item": "Eye protection", "detected": False, "required": True},
    ],
    "hazards": [
        {
            "hazard": "Missing safety harness during elevated work",
            "severity": "High",
            "remedy": "Enforce harness use with certified anchor points and a buddy system.",
        },
        {
            "hazard": "Improper ladder placement on uneven ground",
            "severity": "Medium",
            "remedy": "Use ladder levelers and conduct competent ladder inspection before use.",
        },
    ],
}

DEMO_CRACK_RESULT = {
    "defect_type": "Settlement",
    "crack_width_mm": 2.4,
    "root_causes": ["Subgrade settlement", "Concrete shrinkage during curing"],
    "recommended_repairs": [
        "Structural re-grouting / underpinning assessment",
        "Epoxy injection for non-structural cracks",
    ],
    "urgency": "High",
}
