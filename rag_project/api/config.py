from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings
import json


class APISettings(BaseSettings):
    # Server
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_debug: bool = Field(default=False, env="API_DEBUG")

    # Metadata
    api_title: str = Field(default="RAG Client Analysis API", env="API_TITLE")
    api_version: str = Field(default="1.0.0", env="API_VERSION")
    api_description: str = Field(default="RESTful API for client profile retrieval, semantic search, and AI-powered decision analysis", env="API_DESCRIPTION")

    # CORS
    api_cors_origins_raw: str = Field(default="[*]", env="API_CORS_ORIGINS")
    api_cors_allow_credentials: bool = Field(default=True, env="API_CORS_ALLOW_CREDENTIALS")

    # Mistral
    mistral_api_key: str = Field(default="", env="MISTRAL_API_KEY")

    # Qdrant
    qdrant_url: str = Field(default="http://localhost:6333", env="API_QDRANT_URL")
    qdrant_collection: str = Field(default="client_profiles", env="API_QDRANT_COLLECTION")
    embedding_model: str = Field(default="mistral-embed", env="API_EMBEDDING_MODEL")

    # Search defaults
    default_top_k: int = Field(default=5, env="API_DEFAULT_TOP_K")
    max_top_k: int = Field(default=100, env="API_MAX_TOP_K")

    # Pagination
    default_limit: int = Field(default=10, env="API_DEFAULT_LIMIT")
    max_limit: int = Field(default=100, env="API_MAX_LIMIT")

    # Timeouts
    llm_timeout: int = Field(default=30, env="API_LLM_TIMEOUT")
    qdrant_timeout: int = Field(default=10, env="API_QDRANT_TIMEOUT")
    agent_timeout: int = Field(default=60, env="API_AGENT_TIMEOUT")

    # Rate limiting
    rate_limit_enabled: bool = Field(default=False, env="API_RATE_LIMIT_ENABLED")
    rate_limit_per_minute: int = Field(default=60, env="API_RATE_LIMIT_PER_MINUTE")

    # API Key auth
    require_api_key: bool = Field(default=False, env="API_REQUIRE_API_KEY")
    api_key: str = Field(default="", env="API_API_KEY")

    def cors_origins(self) -> List[str]:
        raw = self.api_cors_origins_raw
        try:
            # Expect JSON-like list string (e.g., ["*"])
            if isinstance(raw, str):
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return parsed
        except Exception:
            pass
        # Fallback: comma-separated string
        if isinstance(raw, str):
            return [o.strip() for o in raw.split(',') if o.strip()]
        return ["*"]


settings = APISettings()
