"""Pydantic schemas for chat2substack pipeline."""

from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class Message(BaseModel):
    """A single message in the conversation."""
    role: Literal["user", "assistant"]
    text: str


class SourceInfo(BaseModel):
    """Source information for the conversation."""
    type: Literal["shared_html", "manual_text"]
    path: str
    url: Optional[str] = None


class NormalizedConversation(BaseModel):
    """Normalized conversation format."""
    id: str  # ISO8601 timestamp
    source: SourceInfo
    title_hint: str = ""
    messages: List[Message]

    @field_validator('messages')
    @classmethod
    def messages_not_empty(cls, v):
        if not v:
            raise ValueError('Conversation must have at least one message')
        return v


class FurtherReading(BaseModel):
    """Further reading reference."""
    title: str
    url: str = Field(..., pattern=r'^https?://.*')


class SubstackDraft(BaseModel):
    """Final Substack draft schema."""
    title: str = Field(..., max_length=80)
    dek: str = Field(..., max_length=200)
    tldr: List[str] = Field(..., min_length=3, max_length=5)
    tags: List[str] = Field(..., min_length=3, max_length=6)
    body_markdown: str = Field(..., max_length=15000)  # ~1500 words max for comprehensive content
    further_reading: Optional[List[FurtherReading]] = None

    @field_validator('tags')
    @classmethod
    def tags_lowercase(cls, v):
        return [tag.lower().strip() for tag in v]

    @field_validator('body_markdown')
    @classmethod
    def body_word_count(cls, v):
        word_count = len(v.split())
        if word_count > 1400:  # Increased from 900 to 1400 for comprehensive content
            raise ValueError(f'Body exceeds 1400 word limit: {word_count} words')
        return v

    @field_validator('tldr')
    @classmethod
    def tldr_not_empty(cls, v):
        for item in v:
            if not item.strip():
                raise ValueError('TL;DR items cannot be empty')
        return v


class GuardrailResult(BaseModel):
    """Result from guardrail checker."""
    ok: bool
    issues: List[str]
    patch: Optional[str] = None


class RunReport(BaseModel):
    """Final run report metadata."""
    run_id: str
    slug: str
    content_hash: str
    word_counts: dict
    redaction_stats: dict
    created_at: datetime
    draft_url: Optional[str] = None
    errors: List[str] = []
