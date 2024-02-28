from typing import Optional

from pydantic import BaseModel


class ChatItem(BaseModel):
    chatSessionId: str
    question: str
    model: str
    existingQuestionId: Optional[str] = None


class ChatAnalysisItem(BaseModel):
    model: str
    question: str
    data: str
    is_english: bool


class KnowledgeIds(BaseModel):
    embeddingIds: list[str]
    fileType: str
