# RAGAS Integration Guide

## Complete Implementation for Your RAG Project

This guide shows you how to implement and use RAGAS (RAG Assessment) evaluation in your project.

## 📋 What's Been Added

### 1. New Dependencies

- `ragas>=0.1.0` - RAGAS evaluation framework
- `datasets>=2.14.0` - HuggingFace datasets for data handling

### 2. New Module: `evaluation/`

```
evaluation/
├── __init__.py              # Module exports
├── ragas_evaluator.py      # Main evaluator class
├── dataset_builder.py      # Dataset preparation
├── metrics_config.py       # RAGAS metrics setup
├── test_queries.py         # Sample test queries
└── README.md               # Detailed documentation
```

### 3. New Scripts

- `scripts/run_ragas_evaluation.py` - Main evaluation script
- `scripts/evaluate_api_with_ragas.py` - API endpoint evaluation

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd c:\Users\rayen\Desktop\RAG\rag_project
pip install -r requirements.txt
```

### Step 2: Set Up API Keys

Create or update `.env` file in your project root:

```bash
# For Mistral (configured as default since you're using it)
MISTRAL_API_KEY=your-mistral-key-here

# Your existing Qdrant and other configs
QDRANT_URL=...

# Optional: For OpenAI (if you want to switch)
# OPENAI_API_KEY=sk-your-key-here
```

**Note**: This project is pre-configured to use Mistral since you're already using it.

### Step 3: Run Your First Evaluation

```bash
python scripts/run_ragas_evaluation.py
```

This will:

1. Query your RAG system with test queries
2. Collect contexts and generate answers
3. Evaluate using RAGAS metrics
4. Save results to `evaluation/evaluation_results.csv`

## 📊 What RAGAS Measures

### Core Metrics (No Ground Truth Needed)

1. **Faithfulness** (0-1, higher = better)
   - Measures if answers contain only information from retrieved context
   - Detects hallucination
   - Goal: > 0.8

2. **Answer Relevancy** (0-1, higher = better)
   - Measures if answer addresses the question
   - Detects off-topic responses
   - Goal: > 0.7

3. **Context Relevancy** (0-1, higher = better)
   - Measures proportion of retrieved context that's useful
   - Detects noisy retrieval
   - Goal: > 0.6

### Advanced Metrics (Ground Truth Required)

4. **Context Precision** (0-1, higher = better)
   - Measures if relevant docs rank higher than irrelevant
   - Goal: > 0.7

5. **Context Recall** (0-1, higher = better)
   - Measures if all relevant info was retrieved
   - Goal: > 0.7

## 💻 Usage Examples

### Example 1: Basic Evaluation

```python
from evaluation import RAGASEvaluator, DatasetBuilder
from rag_core.pipeline.query_pipeline import QueryPipeline

# Initialize
pipeline = QueryPipeline()
builder = DatasetBuilder()

# Query your RAG system
question = "Find clients with defaults"
results = pipeline.execute(question, top_k=3)

# Extract contexts
contexts = [r['text'] for r in results['results']]

# Add to dataset
builder.add_sample(
    question=question,
    answer="Clients with TARGET=1 have defaults...",
    contexts=contexts
)

# Evaluate
dataset = builder.build_dataset()
evaluator = RAGASEvaluator()
scores = evaluator.evaluate_dataset(dataset)

print(scores)
# Output: {'faithfulness': 0.85, 'answer_relevancy': 0.92, ...}
```

### Example 2: Batch Evaluation

```python
from evaluation import DatasetBuilder, RAGASEvaluator
from rag_core.pipeline.query_pipeline import QueryPipeline

pipeline = QueryPipeline()
builder = DatasetBuilder()

# Multiple test queries
queries = [
    "Find high-risk clients",
    "Show clients with good credit history",
    "List clients with previous defaults"
]

# Process each query
for query in queries:
    results = pipeline.execute(query, top_k=3, verbose=False)
    contexts = [r['text'] for r in results['results']]

    # Simple answer (or use LLM to generate)
    answer = f"Retrieved {len(contexts)} relevant clients"

    builder.add_sample(query, answer, contexts)

# Evaluate all at once
dataset = builder.build_dataset()
evaluator = RAGASEvaluator()
scores = evaluator.evaluate_dataset(dataset, verbose=True)
```

### Example 3: Evaluate with Ground Truth

```python
builder = DatasetBuilder()

builder.add_sample(
    question="What indicates default risk?",
    answer="Default risk is indicated by TARGET=1, overdue payments...",
    contexts=["Context about defaults...", "More context..."],
    ground_truth="Key risk factors: TARGET=1, payment difficulties, low income"
)

dataset = builder.build_dataset()
evaluator = RAGASEvaluator()

# Use ALL metrics including those needing ground truth
from evaluation import get_ragas_metrics
all_metrics = get_ragas_metrics(include_all=True)

scores = evaluator.evaluate_dataset(dataset, metrics=all_metrics)
```

### Example 4: Compare Configurations

```python
from evaluation import RAGASEvaluator, DatasetBuilder

def evaluate_with_top_k(top_k):
    builder = DatasetBuilder()
    pipeline = QueryPipeline()

    for query in test_queries:
        results = pipeline.execute(query, top_k=top_k)
        contexts = [r['text'] for r in results['results']]
        builder.add_sample(query, "answer...", contexts)

    dataset = builder.build_dataset()
    evaluator = RAGASEvaluator()
    return evaluator.evaluate_dataset(dataset, verbose=False)

# Compare different top_k values
results_k3 = evaluate_with_top_k(3)
results_k5 = evaluate_with_top_k(5)

evaluator = RAGASEvaluator()
comparison = evaluator.compare_runs(
    [results_k3, results_k5],
    ["top_k=3", "top_k=5"]
)
print(comparison)
```

### Example 5: Evaluate API Endpoints

```python
# Start your FastAPI server first
# uvicorn api.main:app --reload

# Then run API evaluation
python scripts/evaluate_api_with_ragas.py
```

## 🔧 Integration with Existing Code

### Option 1: Add to Your Existing Scripts

```python
# In any existing script
from evaluation import DatasetBuilder, RAGASEvaluator

# After running queries, add evaluation
builder = DatasetBuilder()
# ... add samples ...
dataset = builder.build_dataset()
evaluator = RAGASEvaluator()
scores = evaluator.evaluate_dataset(dataset)
```

### Option 2: Create Evaluation Endpoint

Add to `api/endpoints/analysis.py`:

```python
from evaluation import RAGASEvaluator, DatasetBuilder

@router.post("/evaluate")
async def evaluate_rag_performance(test_cases: List[dict]):
    """Evaluate RAG system using RAGAS."""
    builder = DatasetBuilder()

    for case in test_cases:
        builder.add_sample(**case)

    dataset = builder.build_dataset()
    evaluator = RAGASEvaluator()
    scores = evaluator.evaluate_dataset(dataset)

    return {"scores": scores}
```

### Option 3: Automated Testing

Create `tests/test_rag_quality.py`:

```python
import pytest
from evaluation import RAGASEvaluator, DatasetBuilder

def test_rag_faithfulness():
    """Test that RAG system has high faithfulness."""
    builder = DatasetBuilder()
    # ... add test samples ...

    dataset = builder.build_dataset()
    evaluator = RAGASEvaluator()
    results = evaluator.evaluate_dataset(dataset)

    assert results['faithfulness'] > 0.7, "Faithfulness too low!"
```

## 📈 Interpreting Results

### Score Ranges

| Metric            | Excellent | Good     | Fair    | Poor |
| ----------------- | --------- | -------- | ------- | ---- |
| Faithfulness      | >0.9      | 0.8-0.9  | 0.6-0.8 | <0.6 |
| Answer Relevancy  | >0.85     | 0.7-0.85 | 0.5-0.7 | <0.5 |
| Context Relevancy | >0.8      | 0.6-0.8  | 0.4-0.6 | <0.4 |
| Context Precision | >0.8      | 0.7-0.8  | 0.5-0.7 | <0.5 |
| Context Recall    | >0.8      | 0.7-0.8  | 0.5-0.7 | <0.5 |

### What to Do with Low Scores

**Low Faithfulness (<0.7):**

- Your system is hallucinating
- Check if answer generation properly uses retrieved context
- Improve prompt engineering for answer generation

**Low Answer Relevancy (<0.6):**

- Answers aren't addressing questions
- Review query understanding logic
- Improve answer generation prompts

**Low Context Relevancy (<0.5):**

- Retrieval is too noisy
- Adjust embedding model or similarity threshold
- Improve metadata filtering
- Tune top_k parameter

**Low Context Precision/Recall (<0.6):**

- Retrieval isn't finding right documents
- Check embedding quality
- Review indexing process
- Consider reranking

## 🎯 Best Practices

1. **Start Simple**: Use basic metrics without ground truth first

2. **Create Good Test Sets**:
   - Diverse query types
   - Cover all use cases
   - Mix easy and hard queries

3. **Iterate**:
   - Evaluate baseline
   - Make improvements
   - Re-evaluate
   - Track changes over time

4. **Save Everything**:

   ```python
   # Save datasets
   builder.save_to_csv("evaluation/test_set_v1.csv")

   # Save results
   evaluator.evaluate_and_save(
       dataset,
       "evaluation/results_2024_01_30.csv"
   )
   ```

5. **Compare Versions**:

   ```python
   results_before = {...}
   results_after = {...}

   evaluator.compare_runs(
       [results_before, results_after],
       ["Before optimization", "After optimization"]
   )
   ```

## 🐛 Troubleshooting

### "OpenAI API key not found"

Set `OPENAI_API_KEY` in your `.env` file

### "Module 'ragas' not found"

Run: `pip install ragas datasets`

### Evaluation is too slow

- Use smaller test sets during development
- Use fewer metrics initially
- Consider using a faster LLM

### Getting low scores everywhere

- Check if your answer generation is working
- Verify contexts are being retrieved
- Print out samples to debug
- Start with 1-2 samples to test

## 📚 Additional Resources

- Full documentation: [evaluation/README.md](evaluation/README.md)
- Sample queries: [evaluation/test_queries.py](evaluation/test_queries.py)
- Example scripts: [scripts/run_ragas_evaluation.py](scripts/run_ragas_evaluation.py)
- RAGAS docs: https://docs.ragas.io/

## 🤝 Need Help?

Common questions:

**Q: Do I need ground truth for all samples?**
A: No! Start with faithfulness, answer_relevancy, and context_relevancy which don't need it.

**Q: How many samples do I need?**
A: Start with 5-10 for quick iteration, use 50+ for reliable metrics.

**Q: Can I use Mistral instead of OpenAI?**
A: Yes! RAGAS supports multiple LLM providers. Configure in evaluator initialization.

**Q: How often should I run evaluation?**
A: Run after any major changes to retrieval, embeddings, or answer generation.

## 🎉 Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Set up API keys in `.env`
3. Run basic evaluation: `python scripts/run_ragas_evaluation.py`
4. Review results in `evaluation/evaluation_results.csv`
5. Iterate and improve your RAG system!
