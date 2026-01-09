"""Pydantic 데이터 모델 정의."""

import hashlib
from datetime import datetime

from pydantic import BaseModel, Field, computed_field


class DocumentItem(BaseModel):  # type: ignore[misc]
    """크롤링된 문서 데이터 모델.

    PRD 스키마:
    - id: URL의 MD5 Hash (자동 계산)
    - source: 문서 출처 (python, fastapi 등)
    - version: 프레임워크 버전
    - url: 원본 문서 URL
    - title: 문서 제목
    - content_markdown: 정제된 Markdown 본문
    - content_hash: 본문 SHA256 Hash (변경 감지용)
    - last_updated_at: 문서 내 명시된 수정일
    - crawled_at: 실제 수집 시간
    """

    source: str = Field(description="문서 출처 (python, fastapi 등)")
    version: str = Field(description="프레임워크 버전")
    url: str = Field(description="원본 문서 URL")
    title: str = Field(description="문서 제목")
    content_markdown: str = Field(description="정제된 Markdown 본문")
    last_updated_at: str | None = Field(
        default=None, description="문서 내 명시된 수정일"
    )
    crawled_at: datetime = Field(
        default_factory=datetime.now, description="실제 수집 시간"
    )

    @computed_field  # type: ignore[misc]
    @property
    def id(self) -> str:
        """URL 기반 MD5 해시 ID."""
        return hashlib.md5(self.url.encode()).hexdigest()

    @computed_field  # type: ignore[misc]
    @property
    def content_hash(self) -> str:
        """본문 SHA256 해시 (변경 감지용)."""
        return hashlib.sha256(self.content_markdown.encode()).hexdigest()
