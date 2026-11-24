from __future__ import annotations

import pytest

from rag_eval.contracts import EvalSample, Prediction
from rag_eval.judges.base import LLMJudge
from rag_eval.judges.openai_compatible import OpenAICompatibleJudge


def _sample() -> EvalSample:
    return EvalSample(id="q1", query="capital?", task="generation")


def _prediction() -> Prediction:
    return Prediction(sample_id="q1", answer="Paris")


def _judge(invoke) -> OpenAICompatibleJudge:
    return OpenAICompatibleJudge(
        model="judge-model",
        prompt_version="judge-v1",
        invoke=invoke,
    )


def test_judge_parses_plain_json_response() -> None:
    judge = _judge(
        lambda prompt: '{"score": 0.75, "rationale": "证据与答案一致"}'
    )

    result = judge.judge(_sample(), _prediction())

    assert isinstance(judge, LLMJudge)
    assert result.metric == "answer_correctness"
    assert result.score == 0.75
    assert result.rationale == "证据与答案一致"
    assert result.parse_status == "ok"
    assert result.model == "judge-model"
    assert result.prompt_version == "judge-v1"


def test_judge_parses_fenced_json_with_surrounding_text() -> None:
    judge = _judge(
        lambda prompt: (
            "评审结果如下：\n"
            '```json\n{"score": "0.8", "rationale": 123}\n```\n'
            "以上为最终结果。"
        )
    )

    result = judge.judge(_sample(), _prediction())

    assert result.score == 0.8
    assert result.rationale == "123"
    assert result.parse_status == "ok"


def test_judge_parses_exact_code_fence_response() -> None:
    judge = _judge(
        lambda prompt: (
            '```json\n{"score": 0.6, "rationale": "部分正确"}\n```'
        )
    )

    result = judge.judge(_sample(), _prediction())

    assert result.score == 0.6
    assert result.rationale == "部分正确"
    assert result.parse_status == "ok"


@pytest.mark.parametrize(
    "response",
    [
        "not json",
        '{"score": true, "rationale": "invalid"}',
        '{"score": 1.5, "rationale": "invalid"}',
        '{"score": "NaN", "rationale": "invalid"}',
    ],
)
def test_judge_marks_invalid_responses_as_parse_failed(response: str) -> None:
    result = _judge(lambda prompt: response).judge(_sample(), _prediction())

    assert result.score is None
    assert result.parse_status == "parse_failed"
    assert "解析失败" in result.rationale


def test_judge_marks_invoke_errors_as_call_failed() -> None:
    def invoke(prompt: str) -> str:
        raise RuntimeError("upstream unavailable")

    result = _judge(invoke).judge(_sample(), _prediction())

    assert result.score is None
    assert result.parse_status == "call_failed"
    assert result.rationale == "upstream unavailable"


def test_judge_requires_model_and_prompt_version() -> None:
    with pytest.raises(ValueError, match="model and prompt_version"):
        OpenAICompatibleJudge(
            model="",
            prompt_version="judge-v1",
            invoke=lambda prompt: "{}",
        )
