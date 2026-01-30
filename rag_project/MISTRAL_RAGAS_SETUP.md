# RAGAS Evaluation with Mistral - Quick Setup Guide

## Configuration

Your RAGAS implementation is now configured to use:

- **LLM**: Mistral AI (`mistral-large-latest`)
- **Embeddings**: HuggingFace (`sentence-transformers/all-MiniLM-L6-v2`)
- **Vector DB**: Qdrant (your existing setup)

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:

- `ragas` - Evaluation framework
- `langchain-mistralai` - Mistral integration
- `sentence-transformers` - For embeddings

### 2. Configure API Key

Add your Mistral API key to `.env`:

```bash
MISTRAL_API_KEY=your_mistral_api_key_here
```

Get your Mistral API key from: https://console.mistral.ai/

### 3. Run Evaluation

```bash
python scripts/run_ragas_evaluation.py
```

## Usage Example

```python
from evaluation import RAGASEvaluator, DatasetBuilder
from rag_core.pipeline.query_pipeline import QueryPipeline

# Initialize (uses Mistral by default)
pipeline = QueryPipeline()
builder = DatasetBuilder()
evaluator = RAGASEvaluator()  # Automatically uses Mistral + HuggingFace

# Query your RAG system
results = pipeline.execute("Find high-risk clients", top_k=3)
contexts = [r['text'] for r in results['results']]

# Build evaluation dataset
builder.add_sample(
    question="Find high-risk clients",
    answer="Based on retrieved data...",
    contexts=contexts
)

# Evaluate
dataset = builder.build_dataset()
scores = evaluator.evaluate_dataset(dataset)

print(scores)
# Output: {'faithfulness': 0.85, 'answer_relevancy': 0.92, ...}
```

## What Gets Evaluated

The RAGAS metrics assess your RAG pipeline using Mistral to judge:

1. **Faithfulness** - Does the answer stick to retrieved facts?
2. **Answer Relevancy** - Does the answer address the question?
3. **Context Relevancy** - Are retrieved contexts useful?
4. **Context Precision** - Are relevant docs ranked higher? (requires ground truth)
5. **Context Recall** - Was all relevant info retrieved? (requires ground truth)

## Why Mistral + HuggingFace?

- **Mistral**: You're already using it, so no new API needed
- **HuggingFace Embeddings**: Free, runs locally, no OpenAI dependency
- **Cost-effective**: No additional API costs beyond your existing Mistral usage

## Example Output

```
✅ RAGASEvaluator initialized with Mistral (mistral-large-latest)
   Loading HuggingFace embeddings (sentence-transformers/all-MiniLM-L6-v2)...
   ✅ Embeddings loaded

================================================================================
RAGAS Evaluation Results
================================================================================

📊 FAITHFULNESS
   Score: 0.8500
   Measures if the answer is factually consistent with the retrieved context...

📊 ANSWER_RELEVANCY
   Score: 0.9200
   Measures how relevant and to-the-point the answer is to the question...

📊 CONTEXT_RELEVANCY
   Score: 0.7800
   Measures what proportion of the retrieved context is relevant...
```

## Troubleshooting

### "MISTRAL_API_KEY not found"

Add it to your `.env` file:

```bash
MISTRAL_API_KEY=your_key_here
```

### "Module 'sentence-transformers' not found"

Install dependencies:

```bash
pip install sentence-transformers
```

### Slow first run

HuggingFace embeddings download model on first run (~80MB). Subsequent runs are fast.

### Out of memory

The embedding model runs locally. If you have memory issues:

```python
evaluator = RAGASEvaluator(
    llm_provider="mistral",
    embeddings_model="openai"  # Use OpenAI embeddings instead
)
```

## Advanced Configuration

### Use Different Mistral Model

```python
from langchain_mistralai import ChatMistralAI

evaluator = RAGASEvaluator()
evaluator.llm = ChatMistralAI(
    model="mistral-medium",  # or mistral-small for faster/cheaper
    api_key=os.getenv("MISTRAL_API_KEY")
)
```

### Use Different Embedding Model

```python
from langchain_community.embeddings import HuggingFaceEmbeddings

evaluator = RAGASEvaluator()
evaluator.embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
```

## Integration with Your Existing Code

Your existing RAG pipeline with Qdrant works exactly as before. RAGAS evaluation is a separate layer:

```
User Query
    ↓
[Your RAG Pipeline] ← Uses Qdrant + Mistral (existing)
    ↓
Results (contexts + answers)
    ↓
[RAGAS Evaluation] ← Uses Mistral + HuggingFace (new)
    ↓
Quality Metrics
```

## Next Steps

1. ✅ Verify Mistral API key is set
2. ✅ Run basic evaluation: `python scripts/run_ragas_evaluation.py`
3. ✅ Check results in `evaluation/evaluation_results.csv`
4. ✅ Iterate and improve your RAG system based on metrics

## Resources

- Mistral API: https://docs.mistral.ai/
- RAGAS Docs: https://docs.ragas.io/
- Your Integration Guide: [RAGAS_INTEGRATION_GUIDE.md](RAGAS_INTEGRATION_GUIDE.md)
