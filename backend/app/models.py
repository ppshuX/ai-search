from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)


class SearchResult(BaseModel):
    id: int
    title: str
    url: str
    content: str = ""
    score: float | None = None
    favicon: str | None = None
    raw_content: str | None = None


class Source(BaseModel):
    id: int
    title: str
    url: str


class RelatedQuestions(BaseModel):
    questions: list[str]
