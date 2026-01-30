# RAGAS Evaluation Module

This module provides comprehensive evaluation tools for the RAG system using the RAGAS (RAG Assessment) framework.

## What is RAGAS?

RAGAS is a framework to evaluate Retrieval Augmented Generation (RAG) systems. It provides metrics to measure:

- **Faithfulness**: Whether the generated answer is factually consistent with the retrieved context
- **Answer Relevancy**: How relevant and to-the-point the answer is to the question
- **Context Precision**: Whether relevant items are ranked higher than irrelevant ones
- **Context Recall**: How much of the ground truth answer is covered by retrieved context
- **Context Relevancy**: What proportion of retrieved context is relevant to the question

## Setup

### 1. Install Dependencies

```bash
pip install ragas datasets
```

Or install all project requirements:

```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys

RAGAS requires an LLM for evaluation. Set up your API keys in a `.env` file:

```bash
# For OpenAI
OPENAI_API_KEY=your_openai_key_here

# For Azure OpenAI
AZURE_OPENAI_API_KEY=your_azure_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here

# For other providers (Mistral, Anthropic, etc.)
MISTRAL_API_KEY=your_mistral_key_here
```

## Quick Start

### Basic Evaluation (No Ground Truth Required)

```python
from evaluation import RAGASEvaluator, DatasetBuilder
from rag_core.pipeline.query_pipeline import QueryPipeline

# Initialize components
pipeline = QueryPipeline()
builder = DatasetBuilder()

# Query your RAG system
question = "Find clients with high income"
rag_results = pipeline.execute(question, top_k=3)

# Extract contexts
contexts = [r['text'] for r in rag_results['results']]

# Add to evaluation dataset
builder.add_sample(
    question=question,
    answer="Based on retrieved data: ...",  # Your generated answer
    contexts=contexts
)

# Build and evaluate
dataset = builder.build_dataset()
evaluator = RAGASEvaluator()
results = evaluator.evaluate_dataset(dataset)
```

### Using Pre-built Script

```bash
python scripts/run_ragas_evaluation.py
```

## Module Structure

```
evaluation/
├── __init__.py                 # Module exports
├── ragas_evaluator.py         # Main evaluator class
├── dataset_builder.py         # Dataset preparation utilities
├── metrics_config.py          # RAGAS metrics configuration
├── test_queries.py            # Sample test queries
└── README.md                  # This file
```

## Usage Examples

### 1. Evaluate with Custom Queries

```python
from evaluation import DatasetBuilder, RAGASEvaluator

builder = DatasetBuilder()

# Add multiple samples
test_cases = [
    {
        "question": "Find high-risk clients",
        "answer": "High-risk clients have TARGET=1...",
        "contexts": ["Client 123 has TARGET=1...", "Client 456..."]
    },
    # ... more cases
]

for case in test_cases:
    builder.add_sample(**case)

# Evaluate
dataset = builder.build_dataset()
evaluator = RAGASEvaluator()
results = evaluator.evaluate_dataset(dataset)
```

### 2. Evaluate with Ground Truth

```python
builder = DatasetBuilder()

builder.add_sample(
    question="What indicates loan default risk?",
    answer="Key indicators include previous payment difficulties...",
    contexts=["Context about defaults...", "More context..."],
    ground_truth="Risk factors include: TARGET=1, overdue payments..."
)

dataset = builder.build_dataset()
evaluator = RAGASEvaluator()

# Use all metrics (including those requiring ground truth)
from evaluation import get_ragas_metrics
metrics = get_ragas_metrics(include_all=True)

results = evaluator.evaluate_dataset(dataset, metrics=metrics)
```

### 3. Compare Different Configurations

```python
from evaluation import RAGASEvaluator

# Run evaluation with different top_k values
results_k3 = evaluate_with_config(top_k=3)
results_k5 = evaluate_with_config(top_k=5)

# Compare
evaluator = RAGASEvaluator()
comparison = evaluator.compare_runs(
    [results_k3, results_k5],
    labels=["top_k=3", "top_k=5"]
)
```

### 4. Save and Load Datasets

```python
builder = DatasetBuilder()

# ... add samples ...

# Save for later
builder.save_to_csv("evaluation/my_test_set.csv")

# Load existing dataset
builder2 = DatasetBuilder()
builder2.load_from_csv("evaluation/my_test_set.csv")
dataset = builder2.build_dataset()
```

## Metrics Explanation

### Without Ground Truth (Basic Metrics)

These metrics can be computed without knowing the "correct" answer:

- **Faithfulness**: Measures hallucination - whether the answer contains only information from the context
- **Answer Relevancy**: Measures if the answer actually addresses the question asked
- **Context Relevancy**: Measures how much of the retrieved context is actually useful

### With Ground Truth (Full Metrics)

These require you to provide expected answers:

- **Context Precision**: Measures if relevant docs are ranked higher
- **Context Recall**: Measures if all relevant information was retrieved

## Best Practices

1. **Start with Basic Metrics**: Use metrics that don't require ground truth to quickly assess system performance

2. **Create Diverse Test Sets**: Include different query types:
   - Profile searches
   - Risk assessments
   - Historical queries
   - Analytical questions

3. **Iterate on Prompts**: Use evaluation results to improve your answer generation prompts

4. **Track Over Time**: Save evaluation results to monitor system improvements

5. **Compare Configurations**: Use comparison tools to A/B test different settings

## Interpreting Results

- **Scores range from 0 to 1** (higher is better)
- **Faithfulness > 0.8**: Good - minimal hallucination
- **Answer Relevancy > 0.7**: Good - answers are on-topic
- **Context Relevancy > 0.6**: Good - retrieval is focused
- **Context Precision/Recall > 0.7**: Good - retrieval is comprehensive and accurate

## Troubleshooting

### "No API key found"

Set up your `.env` file with appropriate API keys (OPENAI_API_KEY, etc.)

### "Dataset must have 'question', 'answer', 'contexts' columns"

Ensure your dataset has all required fields. Use `DatasetBuilder` to construct it properly.

### Evaluation is slow

- Reduce dataset size for quick iterations
- Use fewer metrics initially
- Consider using a faster/cheaper LLM for evaluation

## Advanced: Custom Metrics

You can create custom metrics by following the RAGAS documentation:

```python
from ragas.metrics import Metric

class CustomMetric(Metric):
    # Implement your custom evaluation logic
    pass

# Use in evaluation
results = evaluator.evaluate_dataset(
    dataset,
    metrics=[CustomMetric()]
)
```

## Related Files

- `scripts/run_ragas_evaluation.py` - Main evaluation script
- `evaluation/test_queries.py` - Pre-defined test queries
- `rag_core/pipeline/query_pipeline.py` - RAG pipeline being evaluated

## References

- [RAGAS Documentation](https://docs.ragas.io/)
- [RAGAS GitHub](https://github.com/explodinggradients/ragas)
- [Paper: RAGAS - Automated Evaluation of RAG](https://arxiv.org/abs/2309.15217)
