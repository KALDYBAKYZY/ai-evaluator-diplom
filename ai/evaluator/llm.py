import json
import os
import re

import httpx


class LLMError(RuntimeError):
    pass


class LLMClient:
    def __init__(self, provider: str | None = None, model: str | None = None, api_key: str | None = None, timeout: float = 60.0):
        self.provider = (provider or os.getenv("LLM_PROVIDER", "mock")).lower()
        self.model = model or os.getenv("LLM_MODEL", "mock-1")
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.timeout = timeout

    @property
    def name(self) -> str:
        return f"{self.provider}:{self.model}"

    def complete_json(self, system: str, user: str) -> dict:
        if self.provider == "mock":
            return _mock_response(user)
        if self.provider == "openai":
            text = self._openai(system, user)
        elif self.provider == "gemini":
            text = self._gemini(system, user)
        else:
            raise LLMError(f"Unknown provider: {self.provider}")
        return parse_json(text)

    def _openai(self, system: str, user: str) -> str:
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def _gemini(self, system: str, user: str) -> str:
        response = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
            params={"key": self.api_key},
            json={
                "systemInstruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": user}]}],
                "generationConfig": {"responseMimeType": "application/json"},
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]


def parse_json(text: str) -> dict:
    cleaned = text.strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise LLMError("Model did not return JSON")
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise LLMError(f"Invalid JSON from model: {exc}") from exc


def _mock_response(user: str) -> dict:
    slide_match = re.search(r"\[slide (\d+)\]\n(.+)", user)
    slide_no = int(slide_match.group(1)) if slide_match else None
    quote = slide_match.group(2).strip()[:80] if slide_match else ""
    criteria_codes = re.findall(r"code: (\S+)", user)
    item = {
        "score": 3,
        "justification": "Mock-ответ: критерий раскрыт частично.",
        "evidence": [{"slide_no": slide_no, "quote": quote}] if quote else [],
        "missing": ["Нет подтверждённых данных о клиентах"],
    }
    if len(criteria_codes) > 1:
        return {"criteria": [{"code": code, **item} for code in criteria_codes]}
    if "questions" in user.lower():
        return {"questions": ["Кто ваш первый платящий клиент?", "Как вы считаете стоимость привлечения клиента?"]}
    if "feedback" in user.lower():
        return {"strengths": ["Понятная проблема"], "remarks": ["Не раскрыта бизнес-модель"], "slide_refs": [slide_no] if slide_no else []}
    return item
