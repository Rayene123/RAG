import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pathlib import Path
from dotenv import load_dotenv

from api.config import settings
from api.endpoints.search import router as search_router
from api.endpoints.profile import router as profile_router, router_list as profiles_router
from api.endpoints.analysis import router as analysis_router
from api.endpoints.health import router as health_router
from api.dependencies import get_qdrant_retriever, get_query_router, get_agent_orchestrator

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins(),
    allow_credentials=settings.api_cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health_router)
app.include_router(search_router)
app.include_router(profile_router)
app.include_router(analysis_router)
app.include_router(profiles_router)


@app.get("/")
async def root():
    return {"message": "RAG Client Analysis API", "version": settings.api_version}


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors(), "message": "Invalid request"})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": str(exc), "message": "Internal server error"})


# Startup/shutdown
@app.on_event("startup")
async def on_startup():
    # Load environment variables from rag_project/.env so agents can read MISTRAL_API_KEY
    try:
        env_path = Path(__file__).resolve().parent.parent / ".env"
        load_dotenv(dotenv_path=str(env_path))
        print(f"✅ Environment loaded from {env_path}")
    except Exception as e:
        print(f"⚠️  Failed to load .env: {e}")

    # Initialize singletons and test basic connectivity
    retriever = get_qdrant_retriever()
    router = get_query_router()
    orchestrator = get_agent_orchestrator()
    try:
        _ = retriever.get_collection_stats()
        print("✅ Qdrant connection OK")
    except Exception as e:
        print(f"⚠️  Qdrant connection issue: {e}")
    print("✅ QueryRouter and AgentOrchestrator initialized")


@app.on_event("shutdown")
async def on_shutdown():
    print("🔻 API shutdown")


if __name__ == "__main__":
    uvicorn.run("api.main:app", host=settings.api_host, port=settings.api_port, reload=True)
