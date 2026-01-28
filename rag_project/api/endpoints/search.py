from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from api.models.requests import TextSearchRequest, MetadataSearchRequest, HybridSearchRequest
from api.models.responses import SearchResponse, ClientProfile
from api.config import settings
from api.dependencies import get_query_router, get_qdrant_retriever, validate_api_key, rate_limiter

router = APIRouter(prefix="/search", tags=["search"])


def _to_client_profile(result: Dict[str, Any]) -> ClientProfile:
    payload = result.get("metadata") or result.get("payload") or {}
    return ClientProfile(
        client_id=payload.get("client_id") or result.get("client_id"),
        target=payload.get("target") if payload.get("target") is not None else result.get("target", 0),
        text=result.get("text") or payload.get("text", ""),
        metadata=payload,
        score=result.get("score")
    )


@router.post("/text", response_model=SearchResponse)
async def search_text(
    req: TextSearchRequest,
    router_dep = Depends(get_query_router),
    _auth = Depends(validate_api_key),
    _rl = Depends(rate_limiter),
):
    top_k = min(max(req.top_k, 1), settings.max_top_k)
    understanding_info = None
    if req.use_llm_understanding:
        # Parse query via LLM to surface explanation & detected filters
        try:
            from rag_core.query_processor.llm_query_understanding import LLMQueryUnderstanding
            parsed = LLMQueryUnderstanding(llm_provider="mistral").parse_query(req.query)
            understanding_info = {
                "explanation": parsed.get("explanation"),
                "detected_filters": parsed.get("detected_filters", []),
                "intent": parsed.get("intent"),
                "filters": parsed.get("filters", {}),
                "search_query": parsed.get("search_query", req.query),
            }
        except Exception as e:
            understanding_info = {"error": f"LLM understanding failed: {str(e)}"}

    # Use router to perform the actual search (includes LLM understanding if enabled)
    results = router_dep.process_text_query(
        query=req.query,
        top_k=top_k,
        filter_conditions=None,
        enable_query_understanding=req.use_llm_understanding,
    )

    profiles = [_to_client_profile(r) for r in results]
    return SearchResponse(
        results=profiles,
        query=req.query,
        total_results=len(profiles),
        filters_applied=(understanding_info or {}).get("filters"),
        understanding=understanding_info,
    )


@router.post("/metadata", response_model=SearchResponse)
async def search_metadata(
    req: MetadataSearchRequest,
    retriever = Depends(get_qdrant_retriever),
    _auth = Depends(validate_api_key),
    _rl = Depends(rate_limiter),
):
    top_k = min(max(req.top_k, 1), settings.max_top_k)
    # Generic semantic query combined with strict filters
    results = retriever.search(
        query="find clients",
        top_k=top_k,
        filter_conditions=req.filters,
    )
    profiles = [_to_client_profile(r) for r in results]
    return SearchResponse(
        results=profiles,
        query="",
        total_results=len(profiles),
        filters_applied=req.filters,
    )


@router.post("/hybrid", response_model=SearchResponse)
async def search_hybrid(
    req: HybridSearchRequest,
    router_dep = Depends(get_query_router),
    _auth = Depends(validate_api_key),
    _rl = Depends(rate_limiter),
):
    top_k = min(max(req.top_k, 1), settings.max_top_k)
    # Combine explicit filters with LLM-extracted filters
    results = router_dep.process_text_query(
        query=req.query,
        top_k=top_k,
        filter_conditions=req.filters or {},
        enable_query_understanding=True,
    )
    profiles = [_to_client_profile(r) for r in results]
    return SearchResponse(
        results=profiles,
        query=req.query,
        total_results=len(profiles),
        filters_applied=req.filters or {},
    )
