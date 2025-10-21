from __future__ import annotations

from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

try:
    from langchain_community.chat_models import ChatOllama  # type: ignore
except Exception:  # pragma: no cover
    ChatOllama = None  # type: ignore


class LLMClient:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", provider: str = "openai", base_url: Optional[str] = None) -> None:
        self.provider = provider
        if provider == "openai":
            self._chat = ChatOpenAI(model=model, api_key=api_key, temperature=0.2)
        elif provider == "ollama":
            if ChatOllama is None:
                raise RuntimeError("ChatOllama is not available. Install langchain-community and run Ollama.")
            # base_url like http://localhost:11434
            kwargs = {"model": model, "temperature": 0.2}
            if base_url:
                kwargs["base_url"] = base_url
            self._chat = ChatOllama(**kwargs)
        else:
            raise ValueError("Unsupported provider. Use 'openai' or 'ollama'.")

    async def acomplete(self, system: str, prompt: str) -> str:
        messages = [SystemMessage(content=system), HumanMessage(content=prompt)]
        resp = await self._chat.ainvoke(messages)
        return resp.content or ""

    def complete(self, system: str, prompt: str) -> str:
        messages = [SystemMessage(content=system), HumanMessage(content=prompt)]
        resp = self._chat.invoke(messages)
        return resp.content or ""


def enforce_word_limit(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words])
