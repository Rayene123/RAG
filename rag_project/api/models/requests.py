from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class TextSearchRequest(BaseModel):
    query: str = Field(..., description="Natural language query or plain text")
    top_k: int = Field(5, ge=1, le=100)
    use_llm_understanding: bool = Field(True, description="Enable LLM-based query parsing")


class MetadataSearchRequest(BaseModel):
    filters: Dict = Field(..., description="Exact-match and range filters for Qdrant")
    top_k: int = Field(5, ge=1, le=100)


class HybridSearchRequest(BaseModel):
    query: str
    filters: Dict = Field(default_factory=dict)
    top_k: int = Field(5, ge=1, le=100)


class BatchProfileRequest(BaseModel):
    client_ids: List[int]


class ProfileListRequest(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)
    filters: Optional[Dict] = None


class DecisionContext(BaseModel):
    client_id: Optional[int] = None
    decision_type: str
    description: str
    additional_info: Optional[Dict] = None


class Alternative(BaseModel):
    name: str
    description: str
    parameters: Optional[Dict] = None


class AnalysisRequest(BaseModel):
    decision_context: DecisionContext
    query: str
    top_k: int = Field(5, ge=1, le=100)
    alternatives: Optional[List[Alternative]] = None
