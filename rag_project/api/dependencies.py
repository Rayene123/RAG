from typing import Callable, Dict, Any, Optional
from fastapi import Depends, Header, HTTPException
from datetime import datetime, timedelta
from threading import Lock

import os
from api.config import settings
from rag_core.retriever.qdrant_retriever import QdrantRetriever
from rag_core.query_processor.query_router import QueryRouter
from agents.agent_orchestrator import AgentOrchestrator

# Singletons
_retriever_singleton: Optional[QdrantRetriever] = None
_router_singleton: Optional[QueryRouter] = None
_orchestrator_singleton: Optional[AgentOrchestrator] = None

_singleton_lock = Lock()


def get_qdrant_retriever() -> QdrantRetriever:
    global _retriever_singleton
    if _retriever_singleton is None:
        with _singleton_lock:
            if _retriever_singleton is None:
                # Use cloud URL/API key if provided via environment, else local host/port
                cloud_url = os.getenv("API_QDRANT_URL") or None
                cloud_key = os.getenv("API_QDRANT_API_KEY") or None
                _retriever_singleton = QdrantRetriever(
                    url=cloud_url,
                    api_key=cloud_key,
                    collection_name=settings.qdrant_collection,
                )
    return _retriever_singleton


def get_query_router() -> QueryRouter:
    global _router_singleton
    if _router_singleton is None:
        with _singleton_lock:
            if _router_singleton is None:
                # Enable LLM understanding if Mistral key is present in env or settings
                use_llm = bool(os.getenv("MISTRAL_API_KEY") or settings.mistral_api_key)
                # Pass the existing retriever singleton to avoid creating a duplicate
                retriever = get_qdrant_retriever()
                _router_singleton = QueryRouter(retriever=retriever, use_llm_understanding=use_llm)
    return _router_singleton


def get_agent_orchestrator() -> AgentOrchestrator:
    global _orchestrator_singleton
    if _orchestrator_singleton is None:
        with _singleton_lock:
            if _orchestrator_singleton is None:
                _orchestrator_singleton = AgentOrchestrator(model_name="mistral-small-latest")
    return _orchestrator_singleton


# Optional API key validation
async def validate_api_key(x_api_key: Optional[str] = Header(default=None)):
    if not settings.require_api_key:
        return
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# Simple in-memory rate limiter (per IP + path)
_rate_state: Dict[str, Dict[str, Any]] = {}
_rate_lock = Lock()

async def rate_limiter(client_ip: Optional[str] = Header(default=None)):
    if not settings.rate_limit_enabled:
        return

    # Use unknown if not provided
    ip = client_ip or "unknown"
    key = f"{ip}:{datetime.utcnow().minute}"

    with _rate_lock:
        entry = _rate_state.get(key)
        if entry is None:
            _rate_state[key] = {"count": 1, "expires": datetime.utcnow() + timedelta(minutes=1)}
            return
        entry["count"] += 1
        if entry["count"] > settings.rate_limit_per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Cleanup expired keys occasionally
    for k, v in list(_rate_state.items()):
        if v.get("expires") and v["expires"] < datetime.utcnow():
            _rate_state.pop(k, None)
