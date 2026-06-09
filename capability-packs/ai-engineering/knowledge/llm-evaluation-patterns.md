# LLM Evaluation Framework Patterns

**Type**: Engineering Pattern  
**Stack**: LangSmith, RAGAS, DeepEval, AWS Bedrock model evaluation

---

## Why LLM Evaluation Is Non-Negotiable

Unlike traditional software, LLMs fail silently and gradually:
- Prompt changes → output quality degrades without exceptions
- Model version upgrades → regression in specific task types
- RAG retrieval changes → hallucination rate increases
- No static test suite catches these — you need eval pipelines

**Rule**: Every LLM feature ships with an eval dataset and automated quality gate.

---

## Evaluation Dimensions

| Dimension | Question | Tool |
|---|---|---|
| **Faithfulness** | Does the answer stick to the retrieved context? | RAGAS |
| **Answer relevance** | Does the answer address the question? | RAGAS |
| **Context recall** | Did retrieval find all necessary information? | RAGAS |
| **Context precision** | Are the retrieved chunks actually relevant? | RAGAS |
| **Hallucination rate** | Does the model invent facts? | DeepEval |
| **Toxicity** | Does the output contain harmful content? | Perspective API / Bedrock Guardrails |
| **Latency P95** | What's the 95th percentile response time? | CloudWatch / LangSmith |
| **Cost per query** | Token spend per user interaction | Bedrock CloudWatch metrics |

---

## Pattern 1: RAGAS for RAG Evaluation

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)
from datasets import Dataset

def evaluate_rag_pipeline(
    questions: list[str],
    ground_truths: list[str],
    rag_fn,          # callable: question → {answer, contexts}
) -> dict:
    results = []
    for q, gt in zip(questions, ground_truths):
        response = rag_fn(q)
        results.append({
            "question":   q,
            "answer":     response["answer"],
            "contexts":   response["contexts"],
            "ground_truth": gt,
        })

    dataset = Dataset.from_list(results)
    scores = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_recall, context_precision],
    )

    # Fail if faithfulness drops below threshold
    if scores["faithfulness"] < 0.85:
        raise EvalFailure(f"Faithfulness {scores['faithfulness']:.2f} below threshold 0.85")

    return scores
```

---

## Pattern 2: LangSmith Tracing + Evaluation

```python
from langchain_core.tracers.langchain import wait_for_all_tracers
from langsmith import Client
from langsmith.evaluation import evaluate as ls_evaluate

ls_client = Client()

# Create a dataset of golden examples
dataset = ls_client.create_dataset("order-assistant-eval-v1")
ls_client.create_examples(
    inputs=[{"question": "What is the status of order #1234?"}],
    outputs=[{"answer": "Order #1234 is in SHIPPED status, dispatched on 2024-01-15."}],
    dataset_id=dataset.id,
)

# Evaluator — LLM-as-judge
def correctness_evaluator(run, example):
    prompt = f"""
    Question: {example.inputs['question']}
    Expected: {example.outputs['answer']}
    Actual:   {run.outputs['answer']}

    Is the actual answer correct and complete? Reply with a score 0.0–1.0 and brief justification.
    Score:"""
    # Call a cheap model for evaluation (Haiku)
    score = judge_llm.invoke(prompt)
    return {"key": "correctness", "score": float(score.strip()[:3])}

results = ls_evaluate(
    lambda inputs: order_assistant(inputs["question"]),
    data="order-assistant-eval-v1",
    evaluators=[correctness_evaluator],
    experiment_prefix="order-assistant-prod",
)
```

---

## Pattern 3: Continuous Eval in CI/CD

```yaml
# .github/workflows/llm-eval.yml
name: LLM Evaluation Gate

on:
  pull_request:
    paths: ['prompts/**', 'rag/**', 'agents/**']

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run RAG evaluation
        env:
          OPENAI_API_KEY:     ${{ secrets.OPENAI_API_KEY }}
          LANGCHAIN_API_KEY:  ${{ secrets.LANGCHAIN_API_KEY }}
          AWS_REGION:         eu-west-1
        run: |
          pip install ragas langsmith boto3 --break-system-packages
          python scripts/run_eval.py --threshold-faithfulness 0.85 --threshold-relevance 0.80

      - name: Comment results on PR
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const results = JSON.parse(fs.readFileSync('eval-results.json'));
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## LLM Eval Results\n| Metric | Score | Threshold | Status |\n|---|---|---|---|\n${
                results.map(r => `| ${r.metric} | ${r.score.toFixed(2)} | ${r.threshold} | ${r.pass ? '✅' : '❌'} |`).join('\n')
              }`
            });
```

---

## Pattern 4: MLflow for LLM Experiment Tracking

```python
import mlflow
from mlflow.models import infer_signature

mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])

with mlflow.start_run(run_name="rag-v2-chunk512-overlap20"):
    # Log parameters
    mlflow.log_params({
        "model_id":       "anthropic.claude-3-sonnet-20240229-v1:0",
        "embedding_model": "amazon.titan-embed-text-v2:0",
        "chunk_size":     512,
        "chunk_overlap":  20,
        "top_k":          5,
    })

    # Run evaluation
    scores = evaluate_rag_pipeline(test_questions, ground_truths, rag_pipeline)

    # Log metrics
    mlflow.log_metrics({
        "faithfulness":       scores["faithfulness"],
        "answer_relevancy":   scores["answer_relevancy"],
        "context_recall":     scores["context_recall"],
        "context_precision":  scores["context_precision"],
    })

    # Log the model artifact
    mlflow.pyfunc.log_model(
        "rag_pipeline",
        python_model=rag_pipeline,
        signature=infer_signature(["What is the status of order 123?"], ["Order 123 is SHIPPED"]),
    )

    # Register if scores pass threshold
    if scores["faithfulness"] >= 0.85:
        mlflow.register_model(f"runs:/{mlflow.active_run().info.run_id}/rag_pipeline", "order-rag-prod")
```

---

## Evaluation Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Human-only eval | Doesn't scale; inconsistent | LLM-as-judge for scalable consistency checks; humans for golden set curation |
| Eval on training data | Overfitting — doesn't reflect production queries | Use production query samples (anonymised) for eval |
| Single metric | Faithfulness ↑ but relevance ↓ | Always measure ≥3 dimensions |
| One-time eval | Model drift undetected | Scheduled eval (weekly) + CI gate on prompt changes |
| Ignoring latency | P95 latency > SLA → poor UX | Always include latency in eval dashboard |
