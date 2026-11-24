"""最小化的 OpenAI 兼容评审边界。

核心包刻意不引入 HTTP 依赖。应用可以注入自己的请求处理函数。
"""

from __future__ import annotations

import json
import math
from collections.abc import Callable
from typing import Any

from rag_eval.contracts import EvalSample, Prediction
from rag_eval.judges.base import JudgeResult


def _extract_json_object(response: str) -> dict[str, Any]:
    text = response.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        payload = None
    if isinstance(payload, dict):
        return payload

    decoder = json.JSONDecoder()
    for index, character in enumerate(text):
        if character != "{":
            continue
        try:
            candidate, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict):
            return candidate
    raise ValueError("judge response does not contain a JSON object")


def _parse_judge_response(response: str) -> tuple[float, str]:
    if not isinstance(response, str):
        raise ValueError("judge response must be a string")
    payload = _extract_json_object(response)
    score = payload.get("score")
    if isinstance(score, str):
        try:
            score = float(score.strip())
        except ValueError as exc:
            raise ValueError("judge score must be a number between 0 and 1") from exc
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise ValueError("judge score must be a number between 0 and 1")
    numeric_score = float(score)
    if not math.isfinite(numeric_score) or not 0.0 <= numeric_score <= 1.0:
        raise ValueError("judge score must be between 0 and 1")
    rationale = payload.get("rationale", "")
    if rationale is None:
        rationale = ""
    if not isinstance(rationale, str):
        rationale = str(rationale)
    return numeric_score, rationale


class OpenAICompatibleJudge:
    def __init__(
        self,
        *,
        model: str,
        prompt_version: str,
        invoke: Callable[[str], str],
        name: str = "openai-compatible",
    ):
        if not model or not prompt_version:
            raise ValueError("model and prompt_version are required")
        self.name = name
        self.model = model
        self.prompt_version = prompt_version
        self._invoke = invoke

    def judge(self, sample: EvalSample, prediction: Prediction) -> JudgeResult:
        prompt = (
            "Return a JSON object with a score between 0 and 1 and a rationale. "
            f"Question: {sample.query}\nAnswer: {prediction.answer or ''}"
        )
        try:
            response = self._invoke(prompt)
        except Exception as exc:
            return JudgeResult(
                metric="answer_correctness",
                score=None,
                rationale=str(exc),
                parse_status="call_failed",
                model=self.model,
                prompt_version=self.prompt_version,
            )
        try:
            score, rationale = _parse_judge_response(response)
        except (TypeError, ValueError) as exc:
            return JudgeResult(
                metric="answer_correctness",
                score=None,
                rationale=f"{response}\n解析失败: {exc}",
                parse_status="parse_failed",
                model=self.model,
                prompt_version=self.prompt_version,
            )
        return JudgeResult(
            metric="answer_correctness",
            score=score,
            rationale=rationale,
            parse_status="ok",
            model=self.model,
            prompt_version=self.prompt_version,
        )
