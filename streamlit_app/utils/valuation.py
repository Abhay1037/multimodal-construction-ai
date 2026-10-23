"""Cost estimation and real-estate valuation calculations (no external DB dependencies)."""

STRUCTURE_TYPES = {
    "Residential": {
        "label": "Residential",
        "cost_per_sqft_inr": 3500,
        "description": "Independent house / villa construction.",
    },
    "Commercial": {
        "label": "Commercial",
        "cost_per_sqft_inr": 6500,
        "description": "Office / retail / mixed-use building.",
    },
    "Industrial": {
        "label": "Industrial",
        "cost_per_sqft_inr": 5500,
        "description": "Warehouse / factory / logistics facility.",
    },
}

LOCATION_TIERS = {
    "Tier 1": {
        "label": "Tier 1 (Mumbai, Delhi NCR, Bengaluru, Gurugram)",
        "multiplier": 1.0,
    },
    "Tier 2": {
        "label": "Tier 2 (Pune, Hyderabad, Ahmedabad, Chennai)",
        "multiplier": 0.85,
    },
    "Tier 3": {
        "label": "Tier 3 (Jaipur, Lucknow, Kochi, Indore)",
        "multiplier": 0.7,
    },
}

VALUATION_RATE = {
    "Tier 1": 0.88,
    "Tier 2": 0.78,
    "Tier 3": 0.68,
}

MILESTONES = [
    {"id": 1, "name": "Planning & Approvals", "weight": 0.05},
    {"id": 2, "name": "Foundation", "weight": 0.15},
    {"id": 3, "name": "Structural Framing", "weight": 0.2},
    {"id": 4, "name": "MEP Rough-in", "weight": 0.15},
    {"id": 5, "name": "Finishes", "weight": 0.2},
    {"id": 6, "name": "Handover", "weight": 0.25},
]

STEEL_KG_PER_SQFT = 3.5
CEMENT_BAGS_PER_SQFT = 0.45


def compute_valuation(
    *,
    structure_type: str,
    built_up_sqft: float,
    location_tier: str,
    completion_pct: float,
) -> dict:
    """Compute budget, CAPEX, market valuation and resource requirements."""
    spec = STRUCTURE_TYPES[structure_type]
    cost_per_sqft = spec["cost_per_sqft_inr"]
    total_budget = cost_per_sqft * built_up_sqft
    capex_incurred = total_budget * (completion_pct / 100.0)
    market_valuation = capex_incurred * VALUATION_RATE[location_tier]
    steel_tons = (built_up_sqft * STEEL_KG_PER_SQFT) / 1000.0
    cement_bags = built_up_sqft * CEMENT_BAGS_PER_SQFT

    milestone_progress = [
        {
            "id": milestone["id"],
            "name": milestone["name"],
            "progress": round(completion_pct * milestone["weight"], 1),
        }
        for milestone in MILESTONES
    ]

    return {
        "structure_type": structure_type,
        "built_up_sqft": built_up_sqft,
        "location_tier": location_tier,
        "completion_pct": completion_pct,
        "total_project_budget_inr": round(total_budget, 2),
        "capital_expenditure_inr": round(capex_incurred, 2),
        "market_asset_valuation_inr": round(market_valuation, 2),
        "steel_requirement_tons": round(steel_tons, 2),
        "cement_requirement_bags": round(cement_bags, 0),
        "milestone_progress": milestone_progress,
    }


def format_inr(value_inr: float) -> str:
    """Format INR value as Crores when >= 1 Cr, otherwise Lakhs."""
    value = float(value_inr or 0.0)
    if value >= 10000000:
        return f"₹{value / 10000000:.2f} Crores"
    if value >= 100000:
        return f"₹{value / 100000:.2f} Lakhs"
    return f"₹{value:,.0f}"
