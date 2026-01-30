# ⚖️ Decision Shadows - Multimodal RAG System

> **AI-Powered Pre-Decision Analysis Platform** | Generate and evaluate all possible decision alternatives before committing to a choice

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-1.7.0+-red.svg)](https://qdrant.tech/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31.0-FF4B4B.svg)](https://streamlit.io/)

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Platform Access](#-platform-access)
- [Key Features](#-key-features)
- [Technologies Used](#-technologies-used)
- [System Architecture](#-system-architecture)
- [Qdrant Integration](#-qdrant-integration-deep-dive)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Usage Examples](#-usage-examples)
- [API Documentation](#-api-documentation)
- [Evaluation & Metrics](#-evaluation--metrics)

---

## 🎯 Project Overview

**Decision Shadows** is an enterprise-grade multimodal RAG (Retrieval-Augmented Generation) system designed for **financial risk assessment and pre-decision analysis**. The system analyzes loan applications by generating multiple decision alternatives (approve/reject/conditional/defer) and evaluating them against historical cases stored in a vector database.

### Problem Statement

Traditional decision-making systems provide binary recommendations without exploring alternatives. Decision makers lack:

- **Historical context** from similar past cases
- **Risk quantification** for each possible decision path
- **Transparent explanations** for AI recommendations
- **Multi-modal analysis** combining structured data, documents, and images

### Solution

Decision Shadows addresses these challenges by:

1. **Generating shadow decisions** - Creating 4 alternative scenarios for every decision
2. **Semantic search** - Finding similar historical cases using Qdrant vector database
3. **Multi-agent analysis** - Historian and Risk agents provide specialized insights
4. **Explainable AI** - Clear reasoning for every recommendation with supporting evidence

### Target Users

- 💼 **Financial Analysts** - Loan approval decisions
- ⚠️ **Risk Officers** - Portfolio risk assessment
- 📊 **Compliance Teams** - Regulatory adherence validation
- 🏦 **Credit Managers** - Credit policy optimization

---

## 🌐 Platform Access

### Web Dashboard (Streamlit)

```bash
streamlit run web_integration/app.py
```

**URL**: `http://localhost:8501`

**Features**:

- Interactive decision analysis interface
- Client profile search and comparison
- Real-time risk scoring visualization
- Similar cases exploration
- Multi-modal document upload (PDF, images)

### REST API (FastAPI)

```bash
uvicorn api.main:app --reload --port 8000
```

**API Base URL**: `http://localhost:8000`  
**API Documentation**: `http://localhost:8000/docs` (Swagger UI)  
**Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)

### Key Endpoints

- `GET /health` - System health check
- `POST /search/text` - Semantic text search
- `GET /profile/{client_id}` - Retrieve client profile
- `POST /analysis/complete` - Full decision analysis with agents
- `POST /analysis/historian` - Historical pattern analysis
- `POST /analysis/risk` - Risk assessment for alternatives

---

## ✨ Key Features

### Core Capabilities

- ✅ **Shadow Decision Generation** - Automatically generates 4 alternatives per case
- 🔍 **Semantic Search** - Natural language queries across 300K+ client profiles
- 📊 **Risk Scoring** - Quantitative risk assessment (0-10 scale) with default probability
- 🤖 **Multi-Agent System** - Specialized AI agents for history and risk analysis
- 📈 **Similar Cases Retrieval** - Finds top-K most relevant historical precedents
- 🎯 **Explainable AI** - Detailed reasoning and risk factor identification
- 📄 **Multimodal Support** - Process text, PDFs, and images (OCR)

### Advanced Features

- **Metadata Filtering** - Filter by income, age, credit amount, employment type
- **Hybrid Search** - Combines semantic embeddings with metadata constraints
- **Bias Detection** - Identifies decision patterns and potential biases
- **RAGAS Evaluation** - Automated RAG quality assessment
- **Continuous Learning** - System improves from new decisions
- **API-First Design** - RESTful API for seamless integration

---

## 🛠 Technologies Used

### Core Technologies

| Technology                | Version | Purpose                             |
| ------------------------- | ------- | ----------------------------------- |
| **Python**                | 3.10+   | Primary programming language        |
| **Qdrant**                | 1.7.0+  | Vector database for semantic search |
| **FastAPI**               | 0.110.0 | High-performance REST API framework |
| **Streamlit**             | 1.31.0+ | Interactive web dashboard           |
| **Sentence Transformers** | 2.2.0+  | Text embeddings generation          |
| **LangChain**             | 0.1.0+  | LLM orchestration and agents        |
| **Mistral AI**            | Latest  | Large language model (via API)      |

### Data Processing & ML

| Library               | Version | Purpose                               |
| --------------------- | ------- | ------------------------------------- |
| pandas                | 2.0.0+  | Data manipulation and analysis        |
| numpy                 | 1.24.0+ | Numerical computing                   |
| scikit-learn          | 1.3.0+  | Machine learning utilities            |
| sentence-transformers | 2.2.0+  | Embedding model (`all-mpnet-base-v2`) |

### Document Processing

| Library        | Version | Purpose                         |
| -------------- | ------- | ------------------------------- |
| PyMuPDF (fitz) | 1.23.0+ | PDF text extraction             |
| pdfplumber     | 0.10.0+ | PDF table extraction            |
| pytesseract    | 0.3.10+ | OCR for images and scanned PDFs |
| EasyOCR        | 1.7.0+  | Alternative OCR engine          |
| Pillow         | 10.0.0+ | Image processing                |
| opencv-python  | 4.8.0+  | Computer vision preprocessing   |

### Evaluation & Testing

| Library  | Version | Purpose                           |
| -------- | ------- | --------------------------------- |
| RAGAS    | 0.1.0+  | RAG system evaluation             |
| datasets | 2.14.0+ | Dataset management for evaluation |
| tqdm     | 4.65.0+ | Progress bars                     |

### Infrastructure

| Tool          | Purpose                         |
| ------------- | ------------------------------- |
| Docker        | Containerized Qdrant deployment |
| python-dotenv | Environment variable management |
| uvicorn       | ASGI server for FastAPI         |

---

## 🏗 System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                          │
├─────────────────────────────────────────────────────────────────┤
│  Streamlit Dashboard (Port 8501)  │  REST API (Port 8000)       │
│  - Interactive UI                  │  - Swagger Docs             │
│  - Client Profiles                 │  - JSON Endpoints           │
│  - Risk Visualization              │  - External Integration     │
└─────────────────┬───────────────────────────────┬───────────────┘
                  │                               │
                  ▼                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│                   Query Router & Processor                       │
│  - Natural language understanding                                │
│  - Query classification (profile/risk/comparison)                │
│  - Metadata extraction                                           │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SHADOW GENERATOR                             │
├─────────────────────────────────────────────────────────────────┤
│  Generates 4 decision alternatives:                              │
│  ✓ APPROVE          ✓ CONDITIONAL_APPROVE                       │
│  ✓ REJECT           ✓ DEFER                                     │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EMBEDDING LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  Sentence Transformer: all-mpnet-base-v2                         │
│  - Dimension: 768                                                │
│  - Input: Text, OCR from PDFs/Images                             │
│  - Output: Dense vector embeddings                               │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   QDRANT VECTOR DATABASE                         │
├─────────────────────────────────────────────────────────────────┤
│  Collection: credit_clients                                      │
│  - 300,000+ client profiles                                      │
│  - Cosine similarity search                                      │
│  - Hybrid filtering (metadata + semantic)                        │
│  - HNSW index for fast retrieval                                 │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MULTI-AGENT SYSTEM                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐      ┌──────────────────┐                 │
│  │ Historian Agent │      │   Risk Agent     │                  │
│  ├─────────────────┤      ├──────────────────┤                  │
│  │ • Pattern       │      │ • Risk scoring   │                  │
│  │   analysis      │      │ • Default prob   │                  │
│  │ • Trends        │      │ • Risk factors   │                  │
│  │ • Indicators    │      │ • Mitigation     │                  │
│  └─────────────────┘      └──────────────────┘                  │
│                                                                  │
│  Agent Orchestrator (LangChain + Mistral AI)                    │
│  - Coordinates multi-agent workflows                             │
│  - Structured output parsing                                     │
│  - Context management                                            │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OUTPUT LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│  • Decision recommendations with confidence scores               │
│  • Risk assessment (0-10 scale + default probability)            │
│  • Similar cases (top-K results with similarity %)               │
│  • Explainable insights (risk factors, patterns)                 │
│  • Mitigation strategies per alternative                         │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. USER INPUT
   ↓
2. TEXT PREPROCESSING → Embedding Generation (768-dim vector)
   ↓
3. QDRANT SEARCH → Retrieve top-K similar cases (cosine similarity)
   ↓
4. AGENT ORCHESTRATOR
   ├─→ Historian Agent: Analyzes patterns from similar cases
   └─→ Risk Agent: Scores each alternative (APPROVE/REJECT/etc.)
   ↓
5. RESPONSE SYNTHESIS
   ↓
6. DASHBOARD/API RESPONSE

```

---

## 🔍 Qdrant Integration Deep Dive

### Why Qdrant?

Qdrant was chosen as the vector database for Decision Shadows due to:

1. **High Performance** - Handles 300K+ vectors with sub-second query times
2. **Hybrid Search** - Combines semantic similarity with metadata filtering
3. **HNSW Indexing** - Hierarchical Navigable Small World graphs for fast ANN search
4. **Python Native** - First-class Python SDK with type hints
5. **Docker Ready** - Easy deployment and scaling
6. **Cost Effective** - Open-source with no vendor lock-in

### Collection Architecture

**Collection Name**: `credit_clients`

**Vector Configuration**:

```python
{
    "size": 768,                    # Embedding dimension
    "distance": "Cosine",           # Similarity metric
    "on_disk": False                # In-memory for speed
}
```

**Payload Schema**:

```python
{
    "client_id": int,               # Unique identifier
    "text": str,                    # Full text representation
    "target": int,                  # 0=repaid, 1=defaulted

    # Financial Metadata
    "AMT_INCOME_TOTAL": float,      # Annual income
    "AMT_CREDIT": float,            # Loan amount
    "AMT_ANNUITY": float,           # Loan annuity
    "AMT_GOODS_PRICE": float,       # Price of goods

    # Demographic
    "DAYS_BIRTH": int,              # Age (days)
    "CNT_CHILDREN": int,            # Number of children
    "NAME_EDUCATION_TYPE": str,     # Education level
    "NAME_FAMILY_STATUS": str,      # Marital status
    "NAME_INCOME_TYPE": str,        # Income source

    # Credit Bureau Data
    "bureau_credit_active": int,    # Active credits
    "bureau_credit_closed": int,    # Closed credits
    "bureau_days_credit_mean": float,
    "bureau_credit_overdue_mean": float,

    # Previous Applications
    "prev_app_approved": int,       # Approved apps
    "prev_app_refused": int,        # Refused apps

    # Payment History
    "payment_delay_days_mean": float,
    "payment_installment_ratio_mean": float,

    # Additional features (100+ total)
}
```

### Ingestion Pipeline

**Step 1: Data Preprocessing**

```python
# Merge multiple CSV files (application, bureau, payments, etc.)
python preprocessing/merge_and_clean.py

# Feature engineering and text generation
python preprocessing/preprocess_for_rag.py

#sampling
python preprocessing/sample_data.py

# Convert to human-readable text for embeddings
python preprocessing/convert_to_text.py
```

**Step 2: Embedding Generation**

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)
```

**Step 3: Batch Upload to Qdrant**

```python
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams

client = QdrantClient(host="localhost", port=6333)

# Create collection
client.create_collection(
    collection_name="credit_clients",
    vectors_config=VectorParams(size=768, distance=Distance.COSINE)
)

# Upload in batches
batch_size = 100
for i in range(0, len(embeddings), batch_size):
    batch_points = [
        PointStruct(
            id=row['client_id'],
            vector=embedding.tolist(),
            payload=metadata
        )
        for embedding, metadata in zip(batch_embeddings, batch_metadata)
    ]
    client.upsert(collection_name="credit_clients", points=batch_points)
```

### Search Strategies

**1. Pure Semantic Search**

```python
results = retriever.search(
    query="high income professional with good payment history",
    top_k=5
)
```

**2. Hybrid Search (Semantic + Filters)**

```python
results = retriever.search(
    query="stable employment, owns property",
    top_k=10,
    filter_conditions={
        'target': 0,                                    # Only repaid loans
        'AMT_INCOME_TOTAL': {'gte': 50000},            # Income >= $50K
        'NAME_EDUCATION_TYPE': 'Higher education'
    }
)
```

**3. Metadata-Only Search**

```python
results = retriever.search_by_client_profile(
    age=35,
    income=75000,
    education="Higher education",
    family_status="Married",
    top_k=5
)
```

### Performance Metrics

multiple metrics like :
faithfulness : 90%
answer relevancy : 89%

### Qdrant Configuration File

Located at: [config/qdrant_config.py](config/qdrant_config.py)

```python
# Qdrant connection settings
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_HTTPS = False
COLLECTION_NAME = "credit_clients"

# Embedding model settings
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
EMBEDDING_DIMENSION = 768

# Search parameters
DEFAULT_TOP_K = 5
SIMILARITY_THRESHOLD = 0.7

# Batch processing
BATCH_SIZE = 100
MAX_RETRIES = 3
```

### Docker Deployment

**Basic Setup**:

```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

**With Persistence**:

```bash
docker run -d \
    --name qdrant \
    -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```

**Docker Compose** (recommended):

```yaml
version: "3.8"
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333" # REST API
      - "6334:6334" # gRPC
    volumes:
      - ./qdrant_storage:/qdrant/storage
    restart: unless-stopped
```

---

## 📁 Project Structure

```

rag_project/
├── config/ # Qdrant & model settings
├── agents/ # risk agent & analysis agent
├── api/
├── data/
│ ├── raw/ # Original CSV datasets
│ └── processed/ # Cleaned & feature-engineered data
├── embeddings/
│ ├── text/from_structured_data/ # CSV → Text
│ ├── pdf/raw/ & converted/ # PDF documents
│ └── image/raw/ & converted/ # Images (OCR)
├── evaluation/ # evaluating the documents retrieved
├── preprocessing/ # Data transformation scripts
│ ├── pdf_to_text/ # PDF pipeline
│ └── image_to_text/ # Image/OCR pipeline
├── ingestion/
│ ├── ingest_to_qdrant.py # Main ingestion script
│ └── sources/ # Source-specific loaders
├── rag_core/
│ ├── retriever/ # Semantic search (Qdrant)
│ ├── query_processor/ # Input routing & transformation
│ ├── pipeline/ # Shadow generator & orchestration
│ └── utils/
├── agents/ # Historian, Risk, Bias, Explainer agents
└── web_integration/ # Dashboard/API

```

---

## 🔧 Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# 3. Preprocess
install the dataset and load it in the data/raw folder from this link "https://www.kaggle.com/competitions/home-credit-default-risk/data"
python preprocessing/merge_and_clean.py
python preprocessing/preprocess_for_rag.py
python preprocessing/convert_to_text.py

# 4. Ingest to Qdrant
python ingestion/ingest_to_qdrant.py
```

---

## 🚀 Usage

### Basic Retrieval

```python
from rag_core.retriever.qdrant_retriever import QdrantRetriever

retriever = QdrantRetriever()

# Natural language search
results = retriever.search("high income, owns property, good payment history", top_k=5)

# Profile-based
results = retriever.search_by_client_profile(age=35, income=50000, education="Higher education")

# Filtered
results = retriever.search("stable employment", filter_conditions={'target': 0})
```

### Decision Shadows Examples

```python
# 1. Generate shadow decisions
from rag_core.pipeline.shadow_generator import ShadowGenerator
alternatives = ShadowGenerator().generate(client_profile)
# → ['approve', 'reject', 'conditional', 'defer']

# 2. Bias detection
from agents.bias_agent import BiasAgent
bias_report = BiasAgent().analyze_analyst_decisions("analyst_001")

# 3. Counterfactual simulation
results = pipeline.simulate_alternatives(
    original_decision="rejected",
    alternatives=["approve_conditional", "defer"]
)

# 4. Multimodal input
results = pipeline.execute(inputs={
    "application": "app.pdf",
    "income_proof": "payslip.jpg"
})

# 5. Explainable narrative
explanation = ExplainerAgent().generate_decision_narrative(
    decision="approved_conditional",
    alternatives_considered=["approve", "reject", "defer"]
)
```

---

## ⚙️ Configuration

Edit [config/qdrant_config.py](config/qdrant_config.py):

```python
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "credit_clients"
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"  # or all-MiniLM-L6-v2 (faster)
EMBEDDING_DIMENSION = 768  # or 384
```

Edit [.env]:
MISTRAL_API_KEY="Mistral_key"

---

## 📦 Dependencies

**Core**: qdrant-client • sentence-transformers • pandas • numpy • scikit-learn • tqdm

See [requirements.txt](requirements.txt).

---

## 🗺️ Roadmap

**Week 1 (✅)**: Data preprocessing • Qdrant setup • RAG retrieval • Ingestion

**Week 2 (🔄)**: Shadow generator • Multimodal integration • Dashboard • Bias detection • REST API •

**Future**: Real-time streaming • Agent system • Counterfactual reasoning • Compliance validator • Mobile interface

---

## 🔀 Alternative Variants

- **Adaptive Decision DNA**: Compare client "DNA" profiles with past cases
- **Counterfactual Risk Simulator**: "What if?" scenario analysis
- **Regulatory Shadow Analyzer**: Regulatory compliance checking for alternatives

---

## 🐛 Troubleshooting

**Qdrant connection**: `docker ps | grep qdrant` → `docker restart qdrant`

**Out of memory**: Reduce `BATCH_SIZE` in config or use `all-MiniLM-L6-v2` model

---

## 🙏 Acknowledgments

Qdrant • Sentence Transformers • Hugging Face • Hackathon Organizers
