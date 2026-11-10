"""评审协议与标准化评审结果。"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import Field

from rag_eval.contracts import EvalSample, Prediction, StrictModel


class JudgeResult(StrictModel):
    metric: str
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    rationale: str = ""
    parse_status: str = "ok"
    model: str
    prompt_version: str


@runtime_checkable
class LLMJudge(Protocol):
    name: str

    def judge(self, sample: EvalSample, prediction: Prediction) -> JudgeResult:
        """返回校准后的分数，或明确标记为未知/解析失败。"""
