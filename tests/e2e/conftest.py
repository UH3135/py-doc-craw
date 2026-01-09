"""E2E 테스트용 Scrapy fixtures."""

from __future__ import annotations

import json
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest


@dataclass
class CrawlResults:
    """크롤링 결과 컨테이너."""

    items: list[dict[str, Any]] = field(default_factory=list)

    @property
    def urls(self) -> set[str]:
        return {item["url"] for item in self.items}

    @property
    def count(self) -> int:
        return len(self.items)

    def get_by_url(self, url: str) -> dict[str, Any] | None:
        for item in self.items:
            if item.get("url") == url:
                return item
        return None


def _run_spider_crawl(
    version: str = "3.13",
    section: str = "tutorial",
    max_items: int = 3,
) -> list[dict[str, Any]]:
    """subprocess로 Scrapy 스파이더를 실행하고 결과를 반환."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "output.jsonl"

        # Scrapy 명령 실행
        cmd = [
            "uv",
            "run",
            "scrapy",
            "crawl",
            "python",
            "-a",
            f"version={version}",
            "-a",
            f"section={section}",
            "-s",
            f"CLOSESPIDER_ITEMCOUNT={max_items}",
            "-s",
            "LOG_LEVEL=WARNING",
            "-s",
            "HTTPCACHE_ENABLED=True",
            "-o",
            str(output_file),
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Scrapy 크롤링 실패: {result.stderr}")

        # JSONL 파일에서 결과 읽기
        items: list[dict[str, Any]] = []
        if output_file.exists():
            with open(output_file, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        items.append(json.loads(line))

        return items


@pytest.fixture(scope="module")
def spider_crawl_results() -> CrawlResults:
    """Scrapy 스파이더 실행 결과 (3 페이지)."""
    items = _run_spider_crawl(max_items=3)
    return CrawlResults(items=items)


@pytest.fixture
def single_page_result(spider_crawl_results: CrawlResults) -> dict[str, Any]:
    """단일 페이지 결과 (기존 테스트 호환용)."""
    # index.html 우선
    result = spider_crawl_results.get_by_url(
        "https://docs.python.org/3.13/tutorial/index.html"
    )
    if result:
        return result
    return spider_crawl_results.items[0]
