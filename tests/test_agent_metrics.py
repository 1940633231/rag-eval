from __future__ import annotations

import pytest

from rag_eval.contracts import EvalSample, Prediction
from rag_eval.metrics.agent import evaluate_agent


def _sample(sample_id: str, document_id: str) -> EvalSample:
    return EvalSample.model_validate(
        {
            "id": sample_id,
            "task": "agent",
            "query": "query",
            "gold": {
                "documents": [
                    {
                        "document_id": document_id,
                        "relevance": 1,
                    }
                ]
            },
        }
    )


def test_agent_metrics_aggregate_workflow_cost_and_foreign_evidence() -> None:
    samples = [_sample("a", "doc-1"), _sample("b", "doc-2")]
    predictions = [
        Prediction.model_validate(
            {
                "sample_id": "a",
                "documents": [
                    {"document_id": "doc-1", "rank": 1},
                    {"document_id": "doc-2", "rank": 2},
                ],
                "chunks": [
                    {
                        "chunk_id": "chunk-1",
                        "document_id": "doc-1",
                        "rank": 1,
                    }
                ],
                "citations": [
                    {"document_id": "doc-1"},
                    {"document_id": "doc-2"},
                    {"document_id": "doc-3"},
                ],
                "evidence": [
                    {"document_id": "doc-1"},
                    {"document_id": "doc-2"},
                ],
                "latency_ms": 100,
                "usage": {"total_tokens": 120, "cost": 0.25},
                "metadata": {
                    "retry_count": 2,
                    "rewrite_sources": 3,
                    "behavior": "answer",
                },
            }
        ),
        Prediction.model_validate(
            {
                "sample_id": "b",
                "documents": [{"document_id": "doc-2", "rank": 1}],
                "chunks": [
                    {
                        "chunk_id": "chunk-2",
                        "document_id": "doc-2",
                        "rank": 1,
                    }
                ],
                "evidence": [{"document_id": "doc-2"}],
                "latency_ms": 300,
                "usage": {"token_count": 80},
                "metadata": {
                    "behavior": "human_review",
                    "cost": 0.75,
                },
            }
        ),
    ]

    summary = evaluate_agent(samples, predictions, evidence_k=5)

    assert summary.values["retry_count"] == 2.0
    assert summary.values["retry_rate"] == 0.5
    assert summary.values["rewrite_sources"] == 3.0
    assert summary.values["evidence_hit_final"] == 1.0
    assert summary.values["citation_coverage"] == 0.5
    assert summary.values["foreign_evidence_rate"] == pytest.approx(1 / 3)
    assert summary.values["foreign_citation_rate"] == pytest.approx(2 / 3)
    assert summary.values["human_review_rate"] == 0.5
    assert summary.values["latency_p50_ms"] == 200.0
    assert summary.values["latency_p95_ms"] == 290.0
    assert summary.values["token_estimate"] == 200.0
    assert summary.values["cost_estimate"] == 1.0
    assert summary.denominators["latency_p95_ms"] == 2
    assert summary.counts["retry_samples"] == 1
    assert summary.counts["human_review_samples"] == 1
    assert summary.counts["evidence_items"] == 3
    assert summary.counts["citation_items"] == 3


def test_agent_metrics_handle_missing_predictions_and_empty_input() -> None:
    sample = _sample("q1", "doc-1")

    summary = evaluate_agent([sample], [], evidence_k=5)

    assert summary.values["retry_count"] == 0.0
    assert summary.values["evidence_hit_final"] == 0.0
    assert summary.values["latency_p50_ms"] == 0.0
    assert summary.denominators["latency_p95_ms"] == 0
    assert summary.counts["evidence_items"] == 0
    assert evaluate_agent([], []).values == {}


def test_agent_metrics_reject_duplicate_prediction_ids() -> None:
    prediction = Prediction(sample_id="q1")

    with pytest.raises(ValueError, match="duplicate prediction sample_id"):
        evaluate_agent([_sample("q1", "doc-1")], [prediction, prediction])
