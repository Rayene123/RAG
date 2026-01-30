# 🔥 Decision Shadows - Multimodal RAG System

**Hackathon Project** | AI-powered pre-decision analysis system that generates and evaluates all possible alternatives before decisions are made.

## 🎯 Core Concept

Decision Shadows analyzes **all possible decisions before you decide**:

- ✅ Generates shadow decisions (approve/reject/conditional/defer)
- 🔍 Retrieves similar past cases from multimodal memory (text, PDFs, images, numbers)
- 📊 Simulates outcomes for each alternative
- 🎯 Detects biases and decision patterns
- 📝 Provides explainable recommendations

**Target Users**: Financial Analysts • Risk Officers • Compliance Teams

**Key Features**: Shadow generation • Multimodal RAG • Outcome simulation • Explainable AI • Bias detection • Continuous learning • Agent-based analysis

---

## 🏗️ Architecture

```
Input → Query Router → Shadow Generator → Multimodal Embeddings
   → RAG (Qdrant) → Agents (Historian/Risk/Bias/Explainer)
   → Dashboard (Scores/Explanations/Recommendations)
```

**Agents**:

- **Historian**: Analyzes past decision patterns
- **Risk**: Scores risk for each alternative
- **Bias**: Detects decision biases
- **Explainer**: Generates human-readable narratives

---

## 📁 Project Structure

```
rag_project/
├── config/                    # Qdrant & model settings
├── agents/                     # risk agent & analysis agent
├── api/
├── data/
│   ├── raw/                   # Original CSV datasets
│   └── processed/             # Cleaned & feature-engineered data
├── embeddings/
│   ├── text/from_structured_data/    # CSV → Text
│   ├── pdf/raw/ & converted/         # PDF documents
│   └── image/raw/ & converted/       # Images (OCR)
├── evaluation/               # evaluating the documents retrieved
├── preprocessing/             # Data transformation scripts
│   ├── pdf_to_text/          # PDF pipeline
│   └── image_to_text/        # Image/OCR pipeline
├── ingestion/
│   ├── ingest_to_qdrant.py   # Main ingestion script
│   └── sources/              # Source-specific loaders
├── rag_core/
│   ├── retriever/            # Semantic search (Qdrant)
│   ├── query_processor/      # Input routing & transformation
│   ├── pipeline/             # Shadow generator & orchestration
│   └── utils/
├── agents/                    # Historian, Risk, Bias, Explainer agents
└── web_integration/          # Dashboard/API
```

---

## 🔧 Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# 3. Preprocess
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

---

## 🔌 Integration

**PDF/Image Pipelines**:

- Place scripts in `preprocessing/pdf_to_text/` or `preprocessing/image_to_text/`
- Input: `embeddings/{pdf|image}/raw/`
- Output: `embeddings/{pdf|image}/converted/*.txt`

**Custom Agents**:

```python
from agents.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    def analyze(self, decision_context):
        # Your logic
        return result
```

**Shadow Generator**: Customize in `rag_core/pipeline/shadow_generator.py`

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
