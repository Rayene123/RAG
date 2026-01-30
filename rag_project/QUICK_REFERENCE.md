# RAGAS + Mistral + Qdrant - Quick Reference

## Your Setup

- **Vector DB**: Qdrant ✅
- **LLM**: Mistral ✅
- **Evaluation**: RAGAS (now configured with Mistral)

## Installation

```bash
pip install -r requirements.txt
```

## Configuration (.env file)

```bash
# Required for RAGAS evaluation
MISTRAL_API_KEY=your_mistral_key_here

# Your existing Qdrant setup
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_key  # if using cloud
```

## Quick Start

```bash
python scripts/run_ragas_evaluation.py
```

## Code Example

```python
from evaluation import RAGASEvaluator, DatasetBuilder
from rag_core.pipeline.query_pipeline import QueryPipeline

# 1. Initialize (automatically uses Mistral)
pipeline = QueryPipeline()
builder = DatasetBuilder()
evaluator = RAGASEvaluator()

# 2. Run queries
results = pipeline.execute("Find high-risk clients", top_k=3)

# 3. Prepare evaluation data
contexts = [r['text'] for r in results['results']]
builder.add_sample(
    question="Find high-risk clients",
    answer="Generated answer",
    contexts=contexts
)

# 4. Evaluate
dataset = builder.build_dataset()
scores = evaluator.evaluate_dataset(dataset)

# 5. Check scores
print(f"Faithfulness: {scores['faithfulness']:.2f}")
print(f"Answer Relevancy: {scores['answer_relevancy']:.2f}")
print(f"Context Relevancy: {scores['context_relevancy']:.2f}")
```

## Default Configuration

**What RAGAS uses for evaluation:**

- LLM: Mistral (`mistral-large-latest`)
- Embeddings: HuggingFace (`sentence-transformers/all-MiniLM-L6-v2`)

**What your RAG uses (unchanged):**

- Vector DB: Qdrant
- Embeddings: sentence-transformers (your existing setup)
- LLM: Mistral (your existing setup)

## Metrics Explained

| Metric                | What it measures              | Good score |
| --------------------- | ----------------------------- | ---------- |
| **Faithfulness**      | No hallucination              | > 0.8      |
| **Answer Relevancy**  | Answers the question          | > 0.7      |
| **Context Relevancy** | Retrieved contexts are useful | > 0.6      |
| **Context Precision** | Relevant docs ranked higher\* | > 0.7      |
| **Context Recall**    | All relevant info retrieved\* | > 0.7      |

\*Requires ground truth answers

## Common Commands

```bash
# Run basic evaluation
python scripts/run_ragas_evaluation.py

# Evaluate API endpoints
python scripts/evaluate_api_with_ragas.py

# Interactive tutorial
jupyter notebook evaluation/ragas_tutorial.ipynb
```

## File Locations

- **Evaluation Results**: `evaluation/evaluation_results.csv`
- **Test Datasets**: `evaluation/sample_dataset.csv`
- **Configuration**: `evaluation/config.py`
- **Documentation**: `MISTRAL_RAGAS_SETUP.md`

## Integration Pattern

```
┌─────────────────────────────────────────────────┐
│  Your RAG System (Existing)                    │
│  • Qdrant for vector storage                   │
│  • Mistral for generation                      │
│  • sentence-transformers for embeddings        │
└──────────────────┬──────────────────────────────┘
                   │
                   │ produces
                   ▼
           [Contexts + Answers]
                   │
                   │ evaluated by
                   ▼
┌─────────────────────────────────────────────────┐
│  RAGAS Evaluation (New)                        │
│  • Mistral for evaluation judgments            │
│  • HuggingFace for metric embeddings           │
│  • Produces quality scores                     │
└─────────────────────────────────────────────────┘
```

## Troubleshooting

### Issue: "MISTRAL_API_KEY not found"

**Solution**: Add to `.env` file:

```bash
MISTRAL_API_KEY=your_key_here
```

### Issue: First run is slow

**Reason**: HuggingFace downloads embedding model (~80MB) on first run
**Solution**: Wait for download, subsequent runs are fast

### Issue: Want to use OpenAI instead

**Solution**:

```python
evaluator = RAGASEvaluator(
    llm_provider="openai",
    embeddings_model="openai"
)
```

And set `OPENAI_API_KEY` in `.env`

## Advanced Usage

### Compare Configurations

```python
# Test different top_k values
for k in [3, 5, 10]:
    results = evaluate_with_config(top_k=k)
    print(f"top_k={k}: {results}")
```

### Custom Metrics Only

```python
from ragas.metrics import faithfulness, answer_relevancy

evaluator = RAGASEvaluator()
scores = evaluator.evaluate_dataset(
    dataset,
    metrics=[faithfulness, answer_relevancy]
)
```

### Save Results

```python
evaluator.evaluate_and_save(
    dataset,
    output_path="evaluation/my_results.csv"
)
```

## Documentation

- **Complete Guide**: `RAGAS_INTEGRATION_GUIDE.md`
- **Mistral Setup**: `MISTRAL_RAGAS_SETUP.md`
- **Module Docs**: `evaluation/README.md`
- **Tutorial**: `evaluation/ragas_tutorial.ipynb`

## Next Steps

1. ✅ Ensure `MISTRAL_API_KEY` is in `.env`
2. ✅ Run: `python scripts/run_ragas_evaluation.py`
3. ✅ Check results in `evaluation/evaluation_results.csv`
4. ✅ Iterate based on metrics
5. ✅ Track improvements over time

---

**Key Point**: RAGAS uses Mistral to _evaluate_ your RAG system's quality. It doesn't change your existing Qdrant-based RAG pipeline at all!
