# RAG Client Analysis API

A FastAPI-based RESTful API for client profile retrieval, semantic search, and AI-powered decision analysis using Retrieval-Augmented Generation (RAG).

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Setup & Installation](#setup--installation)
- [Configuration: Cloud vs Local](#configuration-cloud-vs-local)
- [Data Ingestion](#data-ingestion)
- [Running the API](#running-the-api)
- [API Endpoints](#api-endpoints)
- [Testing Examples](#testing-examples)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This API provides intelligent access to a client profile database using:
- **Vector Search**: Semantic search powered by sentence transformers
- **Qdrant**: Vector database (supports both Cloud and Local deployment)
- **LLM Integration**: Mistral AI for query understanding and analysis
- **Multi-Agent System**: Historian and Risk agents for decision support

### Key Capabilities

✅ Semantic search across 10,000+ client profiles  
✅ Metadata filtering with 22 indexed fields  
✅ LLM-powered query understanding  
✅ Historical pattern analysis  
✅ Risk assessment with alternatives  
✅ Complete decision analysis workflow  

---

## 🏗️ Architecture

```
api/
├── main.py                    # FastAPI app initialization, CORS, startup/shutdown
├── config.py                  # API settings, environment variables
├── dependencies.py            # Singleton dependencies (retriever, router, agents)
├── endpoints/
│   ├── search.py             # /search/text, /search/metadata, /search/hybrid
│   ├── profile.py            # /profile/{id}, /profiles, /profiles/batch, /profile/{id}/analyzed
│   ├── analysis.py           # /analyze/historical, /analyze/risk, /analyze/complete
│   └── health.py             # /health, /health/qdrant, /metrics
└── models/
    ├── requests.py           # Pydantic request models
    └── responses.py          # Pydantic response models
```

### Data Flow

```
Request → Validation (Pydantic) → Dependencies (Singletons) 
    → Retriever/Router → LLM/Agents → Response Model → JSON
```

---

## ✨ Features

### Search Endpoints
- **Text Search**: Natural language queries with optional LLM understanding
- **Metadata Search**: Filter by demographics, income, occupation, etc.
- **Hybrid Search**: Combine semantic search with explicit filters

### Profile Endpoints
- **Get Profile**: Retrieve single client by ID
- **List Profiles**: Paginated listing with optional filters
- **Batch Retrieval**: Get multiple clients in one request
- **Analyzed Profile**: Complete analysis with similar cases and AI insights

### Analysis Endpoints
- **Historical Analysis**: Pattern discovery from past cases
- **Risk Analysis**: Evaluate alternatives with risk scores
- **Complete Analysis**: Full decision support with historian + risk agents

### Health & Monitoring
- **Health Check**: API status
- **Qdrant Health**: Database connection and collection stats
- **Metrics**: Total clients, vector dimension, distance metric

---

## 🚀 Setup & Installation

### 1. Clone Repository

```bash
cd <project_root>/rag_project
```

### 2. Create Virtual Environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment

Copy and edit the `.env` file (see [Configuration](#configuration-cloud-vs-local) below):

```powershell
# .env is already in rag_project/, just edit it
```

---

## ⚙️ Configuration: Cloud vs Local

The API supports two deployment modes for Qdrant vector database:

### Option 1: Qdrant Cloud (Production)

**When to use**: Production deployment, scalable cloud solution, no local infrastructure

**Setup**:

1. Edit `.env` file:

```env
# ========== Qdrant Configuration ==========
API_QDRANT_URL=https://your-cluster.gcp.cloud.qdrant.io
API_QDRANT_API_KEY=your_api_key_here
API_QDRANT_COLLECTION=client_profiles
```

2. **Important**: Qdrant Cloud requires **payload indexes** on all filtered fields. The ingestion script automatically creates 22 indexes:
   - Integer: `client_id`, `target`, `CNT_CHILDREN`, `CNT_FAM_MEMBERS`, `DAYS_BIRTH`, `DAYS_EMPLOYED`, `ACTIVE_EXTERNAL_CREDITS`
   - Keyword: `CODE_GENDER`, `NAME_FAMILY_STATUS`, `NAME_EDUCATION_TYPE`, `NAME_INCOME_TYPE`, `FLAG_OWN_CAR`, `FLAG_OWN_REALTY`, `NAME_HOUSING_TYPE`, `OCCUPATION_TYPE`, `NAME_CONTRACT_TYPE`
   - Float: `AMT_INCOME_TOTAL`, `AMT_CREDIT`, `OWN_CAR_AGE`, `EXTERNAL_CREDIT_AMOUNT`, `MONTHLY_ANNUITY`, `APPROVAL_RATE`

3. Run ingestion with Cloud env vars (see [Data Ingestion](#data-ingestion))

### Option 2: Local Qdrant (Development)

**When to use**: Local development, testing, no internet dependency

**Setup**:

1. Edit `.env` file:

```env
# ========== Qdrant Configuration ==========
# API_QDRANT_URL=http://localhost:6333
# API_QDRANT_API_KEY=
API_QDRANT_COLLECTION=client_profiles
```

**Note**: Commented out URL means it will use `QDRANT_HOST` and `QDRANT_PORT` from `config/qdrant_config.py`

2. Start local Qdrant (Docker):

```powershell
docker run -p 6333:6333 qdrant/qdrant
```

3. Run ingestion without env vars (see [Data Ingestion](#data-ingestion))

### Mistral API Key

**Required for LLM features**. Get your key from [https://console.mistral.ai/](https://console.mistral.ai/)

```env
# ========== Mistral AI Configuration ==========
MISTRAL_API_KEY=your_mistral_api_key_here
```

---

## 📦 Data Ingestion

The ingestion script loads all 10,000 client profiles with enriched metadata.

### For Qdrant Cloud

```powershell
cd <project_root>

$env:API_QDRANT_URL = "https://your-cluster.gcp.cloud.qdrant.io"
$env:API_QDRANT_API_KEY = "your_api_key_here"

.venv\Scripts\python.exe rag_project\ingestion\ingest_to_qdrant.py
```

**Expected output**:
```
✅ Created collection: client_profiles
✅ Index created: client_id (integer)
✅ Index created: CODE_GENDER (keyword)
...
✅ Ingestion complete!
Total vectors: 10000
```

### For Local Qdrant

```powershell
cd <project_root>

.venv\Scripts\python.exe rag_project\ingestion\ingest_to_qdrant.py
```

**Duration**: ~5-10 minutes for 10,000 profiles (depends on hardware)

---

## 🏃 Running the API

### Start Server

```powershell
cd <project_root>

.venv\Scripts\python.exe -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload --app-dir rag_project
```

### Expected Startup Logs

```
INFO:     Uvicorn running on http://0.0.0.0:8000
✅ Environment loaded from .env
✅ QdrantRetriever initialized
   Connection: https://your-cluster.gcp.cloud.qdrant.io (cloud)
   Collection: client_profiles
✅ Qdrant connection OK
✅ QueryRouter and AgentOrchestrator initialized
```

### Access Points

- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔌 API Endpoints

### Health Endpoints (3)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | API status |
| GET | `/health/qdrant` | Qdrant connection + collection stats |
| GET | `/metrics` | Total clients, vector dimension, distance metric |

### Search Endpoints (3)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/search/text` | Semantic search with optional LLM understanding |
| POST | `/search/metadata` | Filter by metadata fields only |
| POST | `/search/hybrid` | Combine semantic search + metadata filters |

### Profile Endpoints (4)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/profile/{client_id}` | Get single profile by ID |
| GET | `/profiles?offset=0&limit=10` | List profiles (paginated) |
| POST | `/profiles/batch` | Get multiple profiles by IDs |
| GET | `/profile/{client_id}/analyzed` | Profile + similar cases + AI analysis |

### Analysis Endpoints (3)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze/historical` | Historical pattern analysis from similar cases |
| POST | `/analyze/risk` | Risk assessment with alternatives comparison |
| POST | `/analyze/complete` | Full analysis (historian + risk combined) |

---

## 🧪 Testing Examples

### Using PowerShell

#### 1. Health Check

```powershell
Invoke-RestMethod "http://localhost:8000/health"
```

#### 2. Get Profile

```powershell
Invoke-RestMethod "http://localhost:8000/profile/109506"
```

#### 3. Text Search

```powershell
$body = @{
    query = "female manager with high income"
    top_k = 5
    use_llm_understanding = $true
} | ConvertTo-Json

Invoke-RestMethod "http://localhost:8000/search/text" -Method Post -Body $body -ContentType "application/json"
```

#### 4. Hybrid Search with Filters

```powershell
$body = @{
    query = "credit risk assessment"
    filters = @{
        CODE_GENDER = "M"
        NAME_CONTRACT_TYPE = "Cash loans"
    }
    top_k = 5
} | ConvertTo-Json

Invoke-RestMethod "http://localhost:8000/search/hybrid" -Method Post -Body $body -ContentType "application/json"
```

#### 5. List Profiles

```powershell
Invoke-RestMethod "http://localhost:8000/profiles?limit=10"
```

#### 6. Batch Retrieval

```powershell
$body = @{
    client_ids = @(109506, 110157, 115926, 192184, 198341)
} | ConvertTo-Json

Invoke-RestMethod "http://localhost:8000/profiles/batch" -Method Post -Body $body -ContentType "application/json"
```

#### 7. Risk Analysis

```powershell
$body = @{
    decision_context = @{
        client_id = 109506
        decision_type = "loan_approval"
        description = "Risk assessment for loan application"
    }
    alternatives = @(
        @{
            name = "Approve Full Amount"
            description = "Approve $50,000 loan"
            parameters = @{ amount = 50000; term_months = 36 }
        },
        @{
            name = "Approve Reduced"
            description = "Approve $30,000 loan"
            parameters = @{ amount = 30000; term_months = 24 }
        }
    )
    query = "female working professional credit history"
    top_k = 5
} | ConvertTo-Json -Depth 5

Invoke-RestMethod "http://localhost:8000/analyze/risk" -Method Post -Body $body -ContentType "application/json"
```

### Using Postman

1. Import collection from `/docs` interactive page
2. Create environment with `base_url = http://localhost:8000`
3. Run individual requests or entire collection

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Get profile
curl http://localhost:8000/profile/109506

# Text search
curl -X POST http://localhost:8000/search/text \
  -H "Content-Type: application/json" \
  -d '{"query":"female manager","top_k":5,"use_llm_understanding":true}'
```

---

## 🐛 Troubleshooting

### Issue: Server won't start

**Symptoms**: `Address already in use` error

**Solution**:
```powershell
# Kill existing process
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue

# Wait and restart
Start-Sleep -Seconds 2
# Run server command again
```

---

### Issue: "Index required but not found for 'field_name'"

**Symptoms**: 400 Bad Request from Qdrant Cloud on filtered searches

**Cause**: Qdrant Cloud requires explicit indexes on filtered fields (Local Qdrant doesn't)

**Solution**: Re-run ingestion script - it will recreate collection with all 22 indexes

```powershell
$env:API_QDRANT_URL = "https://your-cluster.gcp.cloud.qdrant.io"
$env:API_QDRANT_API_KEY = "your_api_key"
.venv\Scripts\python.exe rag_project\ingestion\ingest_to_qdrant.py
```

---

### Issue: Qdrant connection failed

**Symptoms**: `⚠️ Qdrant connection issue` on startup

**Local Qdrant**:
```powershell
# Check if Docker is running
docker ps

# Start Qdrant if not running
docker run -p 6333:6333 qdrant/qdrant
```

**Cloud Qdrant**:
- Check `.env` has correct `API_QDRANT_URL` and `API_QDRANT_API_KEY`
- Verify cluster is active in Qdrant Cloud console
- Check firewall/network settings

---

### Issue: LLM features not working

**Symptoms**: `LLM understanding failed` or empty analysis responses

**Solution**:
1. Check `MISTRAL_API_KEY` in `.env`
2. Verify key is valid at [https://console.mistral.ai/](https://console.mistral.ai/)
3. Check rate limits if using free tier

---

### Issue: Empty search results

**Symptoms**: Search returns 0 results even though data exists

**Check**:
```powershell
# Verify ingestion
Invoke-RestMethod "http://localhost:8000/metrics"
# Should show: total_clients > 0
```

**Solution**: Re-run ingestion if `total_clients = 0`

---

### Issue: Slow performance

**Optimization tips**:
- Reduce `top_k` in search requests (default: 5)
- Disable `use_llm_understanding` for faster text search
- Use specific filters to reduce search space
- Local Qdrant: Increase Docker memory allocation

---

## 📊 Available Client IDs (Sample)

Valid IDs from the ingested dataset:
```
109506, 110157, 115926, 192184, 198341, 199573, 254373, 276815, 277245, 303601
```

Use these for testing individual profile endpoints.

---

## 🔧 Advanced Configuration

### Custom Timeouts

Edit `.env`:
```env
API_LLM_TIMEOUT=30           # LLM request timeout (seconds)
API_QDRANT_TIMEOUT=10        # Qdrant query timeout
API_AGENT_TIMEOUT=60         # Agent analysis timeout
```

### Rate Limiting

```env
API_RATE_LIMIT_ENABLED=True
API_RATE_LIMIT_PER_MINUTE=60
```

### API Authentication

```env
API_REQUIRE_API_KEY=True
API_API_KEY=your_secret_key_here
```

Then add header to requests:
```powershell
$headers = @{ "X-API-Key" = "your_secret_key_here" }
Invoke-RestMethod "http://localhost:8000/profile/109506" -Headers $headers
```

---

## 📚 Tech Stack

- **API Framework**: FastAPI 0.104+
- **Vector DB**: Qdrant (Cloud or Local)
- **Embeddings**: sentence-transformers/all-mpnet-base-v2 (768-dim)
- **LLM**: Mistral AI (mistral-large-latest)
- **Agent Framework**: Custom multi-agent orchestration
- **Data Processing**: Pandas, NumPy
- **Server**: Uvicorn ASGI

---

## 📝 License

Internal project for RAG-based client analysis.

---

## 👥 Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review startup logs for detailed error messages
3. Verify configuration in `.env` matches your deployment mode (Cloud/Local)

---

**Last Updated**: January 28, 2026
