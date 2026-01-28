from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends
from api.models.requests import AnalysisRequest, Alternative
from api.models.responses import HistoricalAnalysis, RiskAnalysis, CompleteAnalysis
from api.config import settings
from api.dependencies import get_query_router, get_agent_orchestrator, validate_api_key, rate_limiter

router = APIRouter(prefix="/analyze", tags=["analysis"])


@router.post("/historical", response_model=Dict[str, Any])
async def analyze_historical(
    req: AnalysisRequest,
    router_dep = Depends(get_query_router),
    orchestrator = Depends(get_agent_orchestrator),
    _auth = Depends(validate_api_key),
    _rl = Depends(rate_limiter),
):
    similar_cases = router_dep.process_text_query(
        query=req.query,
        top_k=min(max(req.top_k, 1), settings.max_top_k),
        filter_conditions=None,
        enable_query_understanding=True,
    )
    # Use Historian via orchestrator
    result = orchestrator.historian.analyze({
        "decision_context": orchestrator._format_decision_context(req.decision_context.dict()),
        "similar_cases": similar_cases,
    })
    return result


@router.post("/risk", response_model=Dict[str, Any])
async def analyze_risk(
    req: AnalysisRequest,
    router_dep = Depends(get_query_router),
    orchestrator = Depends(get_agent_orchestrator),
    _auth = Depends(validate_api_key),
    _rl = Depends(rate_limiter),
):
    similar_cases = router_dep.process_text_query(
        query=req.query,
        top_k=min(max(req.top_k, 1), settings.max_top_k),
        filter_conditions=None,
        enable_query_understanding=True,
    )
    # Map alternatives to RiskAgent format
    alt_dicts: Optional[List[Dict[str, Any]]] = None
    if req.alternatives:
        alt_dicts = []
        for idx, alt in enumerate(req.alternatives, start=1):
            alt_dicts.append({
                "id": alt.name or f"alt_{idx}",
                "description": alt.description,
                **(alt.parameters or {})
            })

    result = orchestrator.risk.analyze({
        "decision_context": orchestrator._format_decision_context(req.decision_context.dict()),
        "alternatives": alt_dicts or [],
        "similar_cases": similar_cases,
    })
    return result


@router.post("/complete", response_model=CompleteAnalysis)
async def analyze_complete(
    req: AnalysisRequest,
    router_dep = Depends(get_query_router),
    orchestrator = Depends(get_agent_orchestrator),
    _auth = Depends(validate_api_key),
    _rl = Depends(rate_limiter),
):
    similar_cases = router_dep.process_text_query(
        query=req.query,
        top_k=min(max(req.top_k, 1), settings.max_top_k),
        filter_conditions=None,
        enable_query_understanding=True,
    )

    # Map alternatives
    alt_dicts: Optional[List[Dict[str, Any]]] = None
    if req.alternatives:
        alt_dicts = []
        for idx, alt in enumerate(req.alternatives, start=1):
            alt_dicts.append({
                "id": alt.name or f"alt_{idx}",
                "description": alt.description,
                **(alt.parameters or {})
            })

    analysis = orchestrator.analyze_decision(
        decision_context=req.decision_context.dict(),
        similar_cases=similar_cases,
        alternatives=alt_dicts,
    )

    return CompleteAnalysis(**analysis)
