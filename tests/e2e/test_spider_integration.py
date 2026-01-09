"""Scrapy 스파이더 통합 테스트."""

import re

import pytest

from tests.e2e.conftest import CrawlResults


@pytest.mark.e2e
@pytest.mark.slow
class TestSpiderIntegration:
    """실제 Scrapy 스파이더 통합 테스트."""

    def test_crawl_collects_multiple_pages(
        self, spider_crawl_results: CrawlResults
    ) -> None:
        """여러 페이지를 수집하는지 확인."""
        assert spider_crawl_results.count >= 2, (
            f"Expected at least 2 pages, got {spider_crawl_results.count}"
        )

    def test_no_duplicate_urls(self, spider_crawl_results: CrawlResults) -> None:
        """중복 URL이 없는지 확인."""
        url_list = [item["url"] for item in spider_crawl_results.items]
        assert len(url_list) == len(set(url_list)), (
            "Duplicate URLs detected in crawl results"
        )

    def test_all_urls_match_pattern(self, spider_crawl_results: CrawlResults) -> None:
        """모든 URL이 예상 패턴과 일치하는지 확인."""
        pattern = r"https://docs\.python\.org/3\.13/tutorial/.*\.html$"

        for url in spider_crawl_results.urls:
            assert re.match(pattern, url), f"URL doesn't match pattern: {url}"

    def test_each_document_has_required_fields(
        self, spider_crawl_results: CrawlResults
    ) -> None:
        """각 문서에 필수 필드가 있는지 확인."""
        required_fields = {
            "id",
            "source",
            "version",
            "url",
            "title",
            "content_markdown",
            "content_hash",
            "crawled_at",
        }

        for item in spider_crawl_results.items:
            missing = required_fields - set(item.keys())
            assert not missing, f"Missing fields {missing} in {item.get('url')}"

    def test_content_is_not_empty(self, spider_crawl_results: CrawlResults) -> None:
        """각 문서의 content_markdown이 비어있지 않은지 확인."""
        for item in spider_crawl_results.items:
            content = item.get("content_markdown", "")
            assert len(content) > 100, (
                f"Content too short ({len(content)} chars) for {item.get('url')}"
            )


@pytest.mark.e2e
class TestDocumentQuality:
    """개별 문서 품질 검증."""

    def test_markdown_has_headings(self, spider_crawl_results: CrawlResults) -> None:
        """Markdown에 헤딩이 포함되어 있는지 확인."""
        heading_pattern = r"^#{1,6}\s+"

        for item in spider_crawl_results.items:
            content = item.get("content_markdown", "")
            headings = re.findall(heading_pattern, content, re.MULTILINE)
            assert len(headings) >= 1, f"No headings found in {item.get('url')}"

    def test_content_hash_is_valid_sha256(
        self, spider_crawl_results: CrawlResults
    ) -> None:
        """content_hash가 유효한 SHA256 형식인지 확인."""
        sha256_pattern = r"^[a-f0-9]{64}$"

        for item in spider_crawl_results.items:
            content_hash = item.get("content_hash", "")
            assert re.match(sha256_pattern, content_hash), (
                f"Invalid content_hash format: {content_hash[:20]}..."
            )

    def test_source_and_version_are_correct(
        self, spider_crawl_results: CrawlResults
    ) -> None:
        """source와 version이 올바른지 확인."""
        for item in spider_crawl_results.items:
            assert item.get("source") == "python", f"Wrong source: {item.get('source')}"
            assert item.get("version") == "3.13", (
                f"Wrong version: {item.get('version')}"
            )
