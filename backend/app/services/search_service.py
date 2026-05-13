from __future__ import annotations

from typing import Any

from app.config import Settings
from app.models import SearchResult


DEMO_RESULTS = [
    SearchResult(
        id=1,
        title="Tavily Search API for AI agents",
        url="https://docs.tavily.com/",
        content="Tavily provides search results optimized for retrieval augmented generation and AI agents.",
        score=0.97,
    ),
    SearchResult(
        id=2,
        title="DeepSeek API Docs - OpenAI-compatible API",
        url="https://api-docs.deepseek.com/",
        content="DeepSeek exposes OpenAI-compatible chat completion endpoints and supports streaming responses.",
        score=0.94,
    ),
    SearchResult(
        id=3,
        title="FastAPI StreamingResponse",
        url="https://fastapi.tiangolo.com/advanced/custom-response/",
        content="FastAPI can return streaming responses for server-sent events and other incremental payloads.",
        score=0.91,
    ),
]


class SearchService:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def search(self, query: str) -> list[SearchResult]:
        if self.settings.should_use_demo:
            return DEMO_RESULTS

        try:
            from langchain_tavily import TavilySearch
        except ImportError as exc:
            raise RuntimeError(
                "Missing langchain-tavily. Install backend requirements before running live search."
            ) from exc

        tool = TavilySearch(
            max_results=self.settings.tavily_max_results,
            search_depth=self.settings.tavily_search_depth,
            include_raw_content="markdown",
            include_favicon=True,
        )
        payload = await tool.ainvoke({"query": query})
        raw_results = self._extract_results(payload)
        return [self._normalize_result(index + 1, item) for index, item in enumerate(raw_results)]

    @staticmethod
    def _extract_results(payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, dict):
            results = payload.get("results") or payload.get("data") or []
            return results if isinstance(results, list) else []
        if isinstance(payload, list):
            return payload
        return []

    @staticmethod
    def _normalize_result(index: int, item: dict[str, Any]) -> SearchResult:
        return SearchResult(
            id=index,
            title=item.get("title") or "Untitled result",
            url=item.get("url") or "",
            content=item.get("content") or item.get("snippet") or "",
            score=item.get("score"),
            favicon=item.get("favicon"),
            raw_content=item.get("raw_content"),
        )
