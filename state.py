from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel, Field

class NeedTrendMatrix(BaseModel):
    problem: str = Field(description="The core problem identified")
    frequency: str = Field(description="Frequency of the problem in the market")
    emotional_intensity: int = Field(description="1-10 intensity of user pain")
    trend_alignment: str = Field(description="How this aligns with emerging trends")

class CoreEssence(BaseModel):
    name: str
    one_liner: str
    mission: str
    target_audience: str
    core_needs: List[str]

class BusinessModel(BaseModel):
    revenue_streams: List[str]
    potential_risks: List[str]
    tam_sam_som: Dict[str, float]
    strategy: str

class FinancialModel(BaseModel):
    expense_sheet_url: Optional[str] = None
    p_and_l_url: Optional[str] = None
    valuation_benchmark: float = 0.0

class FeatureMap(BaseModel):
    feature_name: str
    description: str
    user_flow_step: int
    figma_component_id: Optional[str] = None

class MarketingBundle(BaseModel):
    platform: str
    copy: str
    scheduled_time: Optional[str] = None
    target_audience: str

class StartupState(TypedDict):
    # Core Inputs
    user_prompt: str
    
    # Phase 2: Discovery
    need_trend_matrix: Optional[List[NeedTrendMatrix]]
    core_essence: Optional[CoreEssence]
    
    # Phase 3: Analytical
    business_model: Optional[BusinessModel]
    financial_model: Optional[FinancialModel]
    
    # Phase 4: Tactical
    feature_maps: Optional[List[FeatureMap]]
    figma_url: Optional[str]
    
    # Phase 5: Marketing
    social_bundles: Optional[List[MarketingBundle]]
    metricool_status: Optional[str]
    
    # Common
    logs: List[str]
    errors: List[str]
    current_step: str
