from datetime import datetime
from fastapi import APIRouter, Depends
from api.models.responses import HealthResponse, MetricsResponse
from api.dependencies import get_qdrant_retriever

router = APIRouter(prefix="", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="healthy", timestamp=datetime.utcnow().isoformat() + "Z")


@router.get("/health/qdrant", response_model=HealthResponse)
async def health_qdrant(retriever = Depends(get_qdrant_retriever)):
    try:
        stats = retriever.get_collection_stats()
        return HealthResponse(status="healthy", timestamp=datetime.utcnow().isoformat() + "Z", qdrant_status=stats)
    except Exception as e:
        return HealthResponse(status="degraded", timestamp=datetime.utcnow().isoformat() + "Z", qdrant_status={"error": str(e)})


@router.get("/metrics", response_model=MetricsResponse)
async def metrics(retriever = Depends(get_qdrant_retriever)):
    stats = retriever.get_collection_stats()
    return MetricsResponse(
        total_clients=stats.get("total_vectors", 0),
        vector_dimension=stats.get("vector_dimension", 0),
        distance_metric=str(stats.get("distance_metric", "")),
    )
