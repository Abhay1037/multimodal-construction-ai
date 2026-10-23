from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class AnalysisType(str, Enum):
    SAFETY_MONITORING = "safety_monitoring"
    CRACK_DETECTION = "crack_detection"


class SafetyStatus(str, Enum):
    SAFE = "Safe"
    WARNING = "Warning"
    HAZARDOUS = "Hazardous"


class SafetyAnalysisResult(BaseModel):
    status: SafetyStatus
    confidence_score: float = Field(ge=0.0, le=100.0)
    summary: str = Field(min_length=1)
    findings: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)


class SiteAnalysisResponse(BaseModel):
    analysis_type: AnalysisType
    result: SafetyAnalysisResult


class ConstructionCategory(str, Enum):
    RESIDENTIAL = "Residential"
    COMMERCIAL = "Commercial"


class PlanEstimateRequest(BaseModel):
    plot_size_sqft: float = Field(gt=0, description="Plot size in square feet")
    budget_usd: float = Field(gt=0, description="Total project budget in USD")
    category: ConstructionCategory = ConstructionCategory.RESIDENTIAL
    timeline_weeks: int = Field(gt=0, description="Estimated project duration in weeks")


class Milestone(BaseModel):
    week: int = Field(ge=1, description="Milestone start week")
    milestone: str = Field(min_length=1)
    tasks: List[str] = Field(default_factory=list)


class PlanEstimateResponse(BaseModel):
    category: ConstructionCategory
    plot_size_sqft: float
    budget_usd: float
    timeline_weeks: int
    estimated_cost_usd: float
    estimated_cost_per_sqft: float
    feasibility: str
    milestones: List[Milestone]


class VisualizationRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=500, description="Construction visualization prompt")
    width: int = Field(default=1024, ge=256, le=2048)
    height: int = Field(default=768, ge=256, le=2048)


class VisualizationResponse(BaseModel):
    image_url: str
    prompt: str
