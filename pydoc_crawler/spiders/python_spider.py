"""Python 공식 문서 스파이더."""

from collections.abc import Iterator
from typing import Any

from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from pydoc_crawler.items import DocumentItem
from pydoc_crawler.parsers.sphinx import SphinxParser


class PythonDocsSpider(CrawlSpider):  # type: ignore[misc]
    """Python 공식 문서 (docs.python.org) 크롤러.

    CrawlSpider를 사용하여 링크를 따라가며 문서를 수집합니다.
    """

    name = "python"
    allowed_domains = ["docs.python.org"]

    # 지원 버전 (3.10 ~ 3.13)
    SUPPORTED_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 0.5,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
    }

    def __init__(
        self,
        version: str = "3.13",
        section: str = "tutorial",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """스파이더 초기화.

        Args:
            version: Python 문서 버전 (기본값: 3.13)
            section: 수집할 섹션 (기본값: tutorial)
        """
        self.version = version
        self.section = section
        self.parser = SphinxParser()

        # 시작 URL 설정
        self.start_urls = [f"https://docs.python.org/{version}/{section}/index.html"]

        # 링크 추출 규칙: 같은 섹션 내의 .html 파일만
        self.rules = (
            Rule(
                LinkExtractor(
                    allow=rf"/{version}/{section}/.*\.html$",
                    deny=(
                        r"/_sources/",
                        r"/genindex",
                        r"/search",
                        r"/py-modindex",
                    ),
                ),
                callback="parse_document",
                follow=True,
            ),
        )

        if version not in self.SUPPORTED_VERSIONS:
            print(
                f"경고: 버전 {version}은 지원 목록에 없습니다. "
                f"지원 버전: {self.SUPPORTED_VERSIONS}"
            )

        super().__init__(*args, **kwargs)

    def parse_document(self, response: Response) -> Iterator[DocumentItem]:
        """문서 페이지 파싱."""
        try:
            result = self.parser.parse(response)

            yield DocumentItem(
                source="python",
                version=self.version,
                url=response.url,
                title=result["title"],
                content_markdown=result["content_markdown"],
                last_updated_at=result.get("last_updated_at"),
            )

        except Exception as e:
            self.logger.error(f"파싱 실패: {response.url} - {e}")
