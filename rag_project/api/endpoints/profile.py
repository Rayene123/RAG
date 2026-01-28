from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from api.models.requests import BatchProfileRequest, ProfileListRequest, DecisionContext, Alternative
from api.models.responses import ClientProfile, ProfileListResponse, AnalyzedProfile, CompleteAnalysis
from api.config import settings
from api.dependencies import get_qdrant_retriever, get_query_router, get_agent_orchestrator, validate_api_key, rate_limiter

router = APIRouter(prefix="/profile", tags=["profile"])
router_list = APIRouter(prefix="/profiles", tags=["profile"])


def _to_client_profile(result: Dict[str, Any]) -> ClientProfile:
    # Extract the full Qdrant payload with enriched fields
    payload = result.get("payload") or result.get("metadata") or {}
    client_id = payload.get("client_id") or result.get("client_id")
    target = payload.get("target") if payload.get("target") is not None else result.get("target", 0)
    text = payload.get("text") or result.get("text", "")
    
    # Debug: Print result structure and payload keys
    if client_id == 109506:
        print(f"DEBUG 109506 - Result keys: {list(result.keys())}")
        print(f"DEBUG 109506 - Payload keys (first 10): {list(payload.keys())[:10]}")
        print(f"DEBUG 109506 - CODE_GENDER from payload: {payload.get('CODE_GENDER')}")
    
    return ClientProfile(client_id=client_id, target=target, text=text, metadata=payload, score=result.get("score"))


@router.get("/{client_id}", response_model=ClientProfile)
async def get_profile(
    client_id: int,
    retriever = Depends(get_qdrant_retriever),
    _auth = Depends(validate_api_key),
    _rl = Depends(rate_limiter),
):
    profile = retriever.get_client_by_id(client_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Client not found")
    return _to_client_profile(profile)


@router.post("/batch", response_model=List[ClientProfile])
async def get_profiles_batch(
    req: BatchProfileRequest,
    retriever = Depends(get_qdrant_retriever),
    _auth = Depends(validate_api_key),
    _rl = Depends(rate_limiter),
):
    results = retriever.get_clients_by_ids(req.client_ids)
    return [_to_client_profile(r) for r in results]


@router_list.get("", response_model=ProfileListResponse)
async def list_profiles(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=settings.default_limit, ge=1, le=settings.max_limit),
    filters: Optional[Dict[str, Any]] = None,
    retriever = Depends(get_qdrant_retriever),
    _auth = Depends(validate_api_key),
    _rl = Depends(rate_limiter),
):
    data = retriever.list_clients(offset=offset, limit=limit, filter_conditions=filters)
    clients = [_to_client_profile(c) for c in data["clients"]]
    return ProfileListResponse(
        clients=clients,
        total=data["total"],
        offset=data["offset"],
        limit=data["limit"],
        returned=data["returned"],
    )


@router.get("/{client_id}/analyzed", response_model=AnalyzedProfile)
async def get_analyzed_profile(
    client_id: int,
    alternatives: Optional[List[Alternative]] = None,
    retriever = Depends(get_qdrant_retriever),
    router_dep = Depends(get_query_router),
    orchestrator = Depends(get_agent_orchestrator),
    _auth = Depends(validate_api_key),
    _rl = Depends(rate_limiter),
):
    # Step 1: Get profile
    profile_raw = retriever.get_client_by_id(client_id)
    if not profile_raw:
        raise HTTPException(status_code=404, detail="Client not found")
    profile = _to_client_profile(profile_raw)

    # Step 2: Similar cases using client's text
    similar_cases = router_dep.process_text_query(
        query=profile.text,
        top_k=settings.default_top_k,
        filter_conditions=None,
        enable_query_understanding=False,
    )

    # Step 3: Run analysis via orchestrator
    decision_context = {
        "client_id": client_id,
        "decision_type": "profile_analysis",
        "description": f"Analyze client {client_id} based on similar cases",
    }

    # Map Alternative models to the format expected by RiskAgent
    alt_dicts: Optional[List[Dict[str, Any]]] = None
    if alternatives:
        alt_dicts = []
        for idx, alt in enumerate(alternatives, start=1):
            alt_dicts.append({
                "id": alt.name or f"alt_{idx}",
                "description": alt.description,
                **(alt.parameters or {})
            })

    analysis = orchestrator.analyze_decision(
        decision_context=decision_context,
        similar_cases=similar_cases,
        alternatives=alt_dicts,
    )

    # Format similar cases into ClientProfile list
    similar_profiles = [_to_client_profile(r) for r in similar_cases]

    return AnalyzedProfile(
        profile=profile,
        similar_cases=similar_profiles,
        analysis=CompleteAnalysis(**analysis),
    )
