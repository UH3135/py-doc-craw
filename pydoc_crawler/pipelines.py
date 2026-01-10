"""Scrapy 파이프라인."""

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import ValidationError
from scrapy import Spider

from pydoc_crawler.items import DocumentItem

logger = logging.getLogger(__name__)


class ValidationPipeline:
    """Pydantic 모델을 통한 데이터 유효성 검증."""

    def __init__(self) -> None:
        self.seen_urls: set[str] = set()

    def process_item(self, item: DocumentItem, spider: Spider) -> dict[str, Any]:
        """아이템 유효성 검증 및 dict 변환."""
        from scrapy.exceptions import DropItem

        try:
            # Pydantic 모델 검증
            if isinstance(item, DocumentItem):
                validated = item
            else:
                validated = DocumentItem(**dict(item))

            # 중복 URL 필터링
            if validated.url in self.seen_urls:
                raise DropItem(f"중복 URL: {validated.url}")
            self.seen_urls.add(validated.url)

            # JSON 직렬화 가능한 dict로 변환
            result: dict[str, Any] = validated.model_dump(mode="json")
            return result

        except ValidationError as e:
            logger.error(f"유효성 검증 실패: {e}")
            raise


class JsonLinesPipeline:
    """JSONL 파일로 저장하는 파이프라인."""

    def __init__(self) -> None:
        self.file: Any = None
        self.items_count = 0

    def open_spider(self, spider: Spider) -> None:
        """스파이더 시작 시 파일 열기."""
        from pydoc_crawler.settings import DATA_DIR

        # data 디렉토리 생성
        Path(DATA_DIR).mkdir(parents=True, exist_ok=True)

        # 출력 파일 경로
        filename = f"{spider.name}_output.jsonl"
        filepath = DATA_DIR / filename

        self.file = open(filepath, "w", encoding="utf-8")  # noqa: SIM115
        logger.info(f"JSONL 출력 파일: {filepath}")

    def close_spider(self, spider: Spider) -> None:
        """스파이더 종료 시 파일 닫기."""
        if self.file:
            self.file.close()
            logger.info(f"총 {self.items_count}개 문서 저장 완료")

    def process_item(self, item: dict[str, Any], spider: Spider) -> dict[str, Any]:
        """아이템을 JSONL로 저장."""
        if self.file:
            line = json.dumps(item, ensure_ascii=False)
            self.file.write(line + "\n")
            self.items_count += 1

        return item


class MarkdownExportPipeline:
    """개별 Markdown 파일로 저장하는 파이프라인 (선택적)."""

    def __init__(self) -> None:
        self.output_dir: Path | None = None

    def open_spider(self, spider: Spider) -> None:
        """스파이더 시작 시 출력 디렉토리 생성."""
        from pydoc_crawler.settings import DATA_DIR

        output_dir = DATA_DIR / "markdown" / spider.name
        output_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = output_dir

    def process_item(self, item: dict[str, Any], spider: Spider) -> dict[str, Any]:
        """아이템을 개별 Markdown 파일로 저장."""
        if not self.output_dir:
            return item

        # 파일명 생성
        content_hash = item.get("content_hash", "")[:8]
        title = item.get("title", "untitled")
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)
        safe_title = safe_title[:50].strip()

        filename = f"{safe_title}_{content_hash}.md"
        filepath = self.output_dir / filename

        # YAML 프론트매터 + 본문
        content = f"""---
title: {item.get("title", "")}
url: {item.get("url", "")}
source: {item.get("source", "")}
version: {item.get("version", "")}
content_hash: {item.get("content_hash", "")}
crawled_at: {item.get("crawled_at", "")}
---

{item.get("content_markdown", "")}
"""

        filepath.write_text(content, encoding="utf-8")
        return item
