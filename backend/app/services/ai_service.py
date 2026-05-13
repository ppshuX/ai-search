from __future__ import annotations

import json
from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from app.config import Settings
from app.models import SearchResult


ANSWER_SYSTEM_PROMPT = """你是 ppshu-ai-search 的 AI 搜索分析助手。
请基于联网搜索结果回答用户问题，要求：
1. 用中文输出，结构清晰，先给结论，再给关键依据。
2. 任何来自搜索结果的事实都必须用 [来源编号] 标注，例如 [1]。
3. 不要编造来源；如果资料不足，明确说明不足之处。
4. 保持客观，区分事实、推断和建议。
"""

RELATED_SYSTEM_PROMPT = """你是搜索助手。基于用户问题和答案，生成 3 到 5 个中文相关追问。
只返回 JSON，格式为 {"questions":["问题1","问题2"]}。不要返回 Markdown。"""


class AIService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = AsyncOpenAI(
            api_key=settings.deepseek_api_key or "demo-key",
            base_url=settings.deepseek_base_url,
        )

    async def stream_answer(self, query: str, results: list[SearchResult]) -> AsyncIterator[str]:
        if self.settings.should_use_demo:
            demo = self._demo_answer(query, results)
            for token in demo.split(" "):
                yield token + " "
            return

        context = self._build_context(results)
        response = await self.client.chat.completions.create(
            model=self.settings.deepseek_model,
            temperature=self.settings.deepseek_temperature,
            stream=True,
            messages=[
                {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"用户问题：{query}\n\n搜索结果上下文：\n{context}\n\n请生成带引用编号的综合回答。",
                },
            ],
        )
        async for chunk in response:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                yield delta

    async def related_questions(self, query: str, answer: str, results: list[SearchResult]) -> list[str]:
        if self.settings.should_use_demo:
            return [
                f"{query} 的最新进展有哪些？",
                f"这个问题有哪些可靠来源可以继续阅读？",
                f"不同资料对 {query} 的结论是否一致？",
            ]

        context = self._build_context(results[:5], max_chars=3500)
        response = await self.client.chat.completions.create(
            model=self.settings.deepseek_model,
            temperature=0.4,
            messages=[
                {"role": "system", "content": RELATED_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"用户问题：{query}\n\n已生成答案：{answer}\n\n搜索上下文：{context}",
                },
            ],
        )
        content = response.choices[0].message.content or "{}"
        return self._parse_questions(content)

    @staticmethod
    def _build_context(results: list[SearchResult], max_chars: int = 9000) -> str:
        chunks = []
        total = 0
        for result in results:
            text = result.raw_content or result.content
            entry = f"[{result.id}] {result.title}\nURL: {result.url}\n摘要: {text}\n"
            if total + len(entry) > max_chars:
                break
            chunks.append(entry)
            total += len(entry)
        return "\n".join(chunks)

    @staticmethod
    def _parse_questions(content: str) -> list[str]:
        try:
            data = json.loads(content.strip())
            questions = data.get("questions", [])
        except json.JSONDecodeError:
            questions = [line.strip("- 0123456789.、") for line in content.splitlines()]
        return [question for question in questions if isinstance(question, str) and question.strip()][:5]

    @staticmethod
    def _demo_answer(query: str, results: list[SearchResult]) -> str:
        refs = ", ".join(f"[{item.id}]" for item in results[:3])
        return (
            f"这是演示模式回答。你搜索的是：{query}。\n\n"
            f"从当前可用资料看，AI 搜索引擎通常由实时检索、上下文组装、模型综合、引用回填和结果列表组成 {refs}。\n\n"
            "上线真实模式时，请在后端环境变量中配置 `TAVILY_API_KEY`、`DEEPSEEK_API_KEY`，"
            "系统会调用 Tavily 获取最新网页结果，再通过 DeepSeek OpenAI 兼容接口流式生成答案。"
        )
