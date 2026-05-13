from __future__ import annotations

import json
import re
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.config import Settings, get_settings
from app.models import SearchRequest
from app.services.ai_service import AIService
from app.services.search_service import SearchService

router = APIRouter()


def sse(event: str, data: object) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.get("/health")
async def health(settings: Settings = Depends(get_settings)) -> dict[str, object]:
    return {
        "ok": True,
        "app": settings.app_name,
        "demoMode": settings.should_use_demo,
        "model": settings.deepseek_model,
    }


@router.post("/search/stream")
async def stream_search(
    request: SearchRequest,
    settings: Settings = Depends(get_settings),
) -> StreamingResponse:
    async def event_stream() -> AsyncIterator[str]:
        answer_parts: list[str] = []
        try:
            yield sse("search_start", {"query": request.query})

            search_service = SearchService(settings)
            results = await search_service.search(request.query)
            yield sse("results", {"results": [item.model_dump() for item in results]})

            ai_service = AIService(settings)
            async for delta in ai_service.stream_answer(request.query, results):
                answer_parts.append(delta)
                yield sse("answer_delta", {"delta": delta})

            answer = "".join(answer_parts)
            if results and not re.search(r"\[\d+\]", answer):
                fallback_citations = " ".join(f"[{item.id}]" for item in results[: min(3, len(results))])
                citation_delta = f"\n\n参考来源：{fallback_citations}"
                answer_parts.append(citation_delta)
                yield sse("answer_delta", {"delta": citation_delta})

            related = await ai_service.related_questions(request.query, "".join(answer_parts), results)
            yield sse("related_questions", {"questions": related})
            yield sse("done", {"ok": True})
        except Exception as exc:
            yield sse("error", {"message": str(exc)})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
