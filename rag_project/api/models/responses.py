from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class ClientProfile(BaseModel):
    client_id: int
    target: int
    text: str
    metadata: Dict[str, Any]
    score: Optional[float] = None


class SearchResponse(BaseModel):
    results: List[ClientProfile]
    query: str
    total_results: int
    filters_applied: Optional[Dict] = None
    understanding: Optional[Dict[str, Any]] = None


class ProfileListResponse(BaseModel):
    clients: List[ClientProfile]
    total: int
    offset: int
    limit: int
    returned: int


class HistoricalAnalysis(BaseModel):
    common_patterns: List[str]
    historical_outcomes: Dict[str, Any]
    key_precedents: List[str]
    notable_differences: List[str]
    risk_indicators: List[str]


class RiskAnalysis(BaseModel):
    alternatives: List[Dict]


class CompleteAnalysis(BaseModel):
    decision_context: Dict
    historian_analysis: Dict
    risk_analysis: Optional[Dict]
    similar_cases_count: int
    avg_similarity: float


class AnalyzedProfile(BaseModel):
    profile: ClientProfile
    similar_cases: List[ClientProfile]
    analysis: CompleteAnalysis


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    qdrant_status: Optional[Dict] = None


class MetricsResponse(BaseModel):
    total_clients: int
    vector_dimension: int
    distance_metric: str
