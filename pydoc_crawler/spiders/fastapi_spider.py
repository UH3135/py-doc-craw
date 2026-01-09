"""FastAPI 공식 문서 스파이더."""

from collections.abc import Iterator
from typing import Any

from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from pydoc_crawler.items import DocumentItem
from pydoc_crawler.parsers.mkdocs import MkDocsParser


class FastAPIDocsSpider(CrawlSpider):
    """FastAPI 공식 문서 (fastapi.tiangolo.com) 크롤러.

    MkDocs Material 기반 문서 사이트를 크롤링합니다.
    """

    name = "fastapi"
    allowed_domains = ["fastapi.tiangolo.com"]

    # 지원 언어
    SUPPORTED_LANGUAGES = ["en", "ko", "ja", "zh", "es", "pt", "ru", "de", "fr"]

    # 섹션 매핑
    SECTIONS = {
        "tutorial": "tutorial",
        "advanced": "advanced",
        "reference": "reference",
        "about": "about",
        "all": "",  # 전체 문서
    }

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 0.5,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
    }

    def __init__(
        self,
        lang: str = "en",
        section: str = "tutorial",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """스파이더 초기화.

        Args:
            lang: 문서 언어 (기본값: en)
            section: 수집할 섹션 (기본값: tutorial)
        """
        self.lang = lang
        self.section = section
        self.parser = MkDocsParser()

        # 시작 URL 설정
        section_path = self.SECTIONS.get(section, section)
        if lang == "en":
            # 영어는 기본 경로
            if section_path:
                self.start_urls = [
                    f"https://fastapi.tiangolo.com/{section_path}/",
                ]
            else:
                self.start_urls = ["https://fastapi.tiangolo.com/"]
        else:
            # 다른 언어는 언어 코드 포함
            if section_path:
                self.start_urls = [
                    f"https://fastapi.tiangolo.com/{lang}/{section_path}/",
                ]
            else:
                self.start_urls = [f"https://fastapi.tiangolo.com/{lang}/"]

        # 링크 추출 규칙
        if lang == "en":
            allow_pattern = rf"/{section_path}/.*" if section_path else r"/.*"
        else:
            allow_pattern = (
                rf"/{lang}/{section_path}/.*" if section_path else rf"/{lang}/.*"
            )

        self.rules = (
            Rule(
                LinkExtractor(
                    allow=allow_pattern,
                    deny=(
                        r"/search/",
                        r"#.*$",  # 앵커 링크 제외
                        r"\?.*$",  # 쿼리 파라미터 제외
                    ),
                ),
                callback="parse_document",
                follow=True,
            ),
        )

        if lang not in self.SUPPORTED_LANGUAGES:
            print(
                f"경고: 언어 {lang}은 지원 목록에 없습니다. "
                f"지원 언어: {self.SUPPORTED_LANGUAGES}"
            )

        super().__init__(*args, **kwargs)

    def parse_document(self, response: Response) -> Iterator[DocumentItem]:
        """문서 페이지 파싱."""
        # 중복 URL 방지 (trailing slash 정규화)
        url = response.url.rstrip("/")

        try:
            result = self.parser.parse(response)

            # 버전 정보 추출 (FastAPI 문서에서)
            version = self._extract_version(response)

            yield DocumentItem(
                source="fastapi",
                version=version,
                url=url,
                title=result["title"],
                content_markdown=result["content_markdown"],
                last_updated_at=result.get("last_updated_at"),
            )

        except Exception as e:
            self.logger.error(f"파싱 실패: {response.url} - {e}")

    def _extract_version(self, response: Response) -> str:
        """FastAPI 버전 정보 추출."""
        # 페이지에서 버전 정보 추출 시도
        version_selector = response.css(".md-version__current::text").get()
        if version_selector:
            return version_selector.strip()

        # 기본값: 언어 코드 반환 (버전 대신)
        return self.lang
