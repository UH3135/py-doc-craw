"""MkDocs Material 문서 파서."""

from typing import Any

from bs4 import BeautifulSoup, Tag
from markdownify import markdownify as md
from scrapy.http import Response


class MkDocsParser:
    """MkDocs Material 기반 문서 사이트 파서.

    대상: FastAPI, Typer, SQLModel 등
    """

    # 본문 영역 CSS 선택자 (우선순위 순)
    CONTENT_SELECTORS = [
        "article.md-content__inner",
        "div.md-content__inner",
        "article",
        "main",
    ]

    # 제거할 노이즈 요소
    NOISE_SELECTORS = [
        "nav",
        ".md-nav",
        ".md-sidebar",
        ".md-header",
        ".md-footer",
        ".md-source",
        ".headerlink",
        ".md-content__button",  # 편집 버튼
        ".md-annotation",  # 주석 팝업
        "script",
        "style",
    ]

    def parse(self, response: Response) -> dict[str, Any]:
        """Scrapy Response를 파싱하여 Markdown으로 변환."""
        soup = BeautifulSoup(response.text, "html.parser")

        title = self._extract_title(soup)
        content_div = self._find_content_area(soup)

        if not content_div:
            raise ValueError(f"본문 영역을 찾을 수 없습니다: {response.url}")

        # 노이즈 제거
        self._remove_noise(content_div)

        # Markdown 변환
        content_markdown = self._to_markdown(content_div)

        # 수정일 추출 (있는 경우)
        last_updated = self._extract_last_updated(soup)

        return {
            "title": title,
            "content_markdown": content_markdown,
            "last_updated_at": last_updated,
        }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """문서 제목 추출."""
        # MkDocs Material: h1.md-content__title 또는 일반 h1
        title_tag = soup.select_one("h1")
        if title_tag:
            # headerlink 제거
            for link in title_tag.select(".headerlink, .md-content__button"):
                link.decompose()
            return str(title_tag.get_text(strip=True))

        # fallback: <title> 태그
        if soup.title:
            # "Title - FastAPI" 형태에서 제목만 추출
            title_text = str(soup.title.get_text(strip=True))
            return title_text.split(" - ")[0].strip()

        return "Untitled"

    def _find_content_area(self, soup: BeautifulSoup) -> Tag | None:
        """본문 영역 찾기."""
        for selector in self.CONTENT_SELECTORS:
            content = soup.select_one(selector)
            if content:
                return content
        return None

    def _remove_noise(self, content: Tag) -> None:
        """노이즈 요소 제거."""
        for selector in self.NOISE_SELECTORS:
            for element in content.select(selector):
                element.decompose()

    def _to_markdown(self, content: Tag) -> str:
        """HTML을 Markdown으로 변환."""
        markdown = md(
            str(content),
            heading_style="ATX",
            code_language_callback=self._detect_code_language,
        )

        # 후처리: 불필요한 빈 줄 정리
        lines = markdown.split("\n")
        cleaned_lines: list[str] = []
        prev_empty = False

        for line in lines:
            is_empty = not line.strip()
            if is_empty and prev_empty:
                continue
            cleaned_lines.append(line)
            prev_empty = is_empty

        return "\n".join(cleaned_lines).strip()

    def _detect_code_language(self, element: Tag) -> str:
        """코드 블록의 언어 감지."""
        # 검사할 요소들: 현재 요소 + 자식 code 태그
        elements_to_check = [element]
        code_child = element.find("code")
        if code_child and isinstance(code_child, Tag):
            elements_to_check.append(code_child)

        for el in elements_to_check:
            # data-language 속성
            if el.get("data-language"):
                return str(el["data-language"])

            # class 속성에서 언어 추출
            classes = el.get("class")
            if classes and isinstance(classes, list):
                for cls in classes:
                    if isinstance(cls, str):
                        # MkDocs Material: language-python, language-bash 등
                        if cls.startswith("language-"):
                            return cls.replace("language-", "")
                        # highlight.js: hljs python 등
                        if cls in (
                            "python",
                            "bash",
                            "shell",
                            "json",
                            "yaml",
                            "sql",
                            "javascript",
                            "typescript",
                        ):
                            return cls

        # MkDocs highlight 클래스 (부모 div)
        parent = element.parent
        if parent and hasattr(parent, "get"):
            parent_classes = parent.get("class")
            if parent_classes and isinstance(parent_classes, list):
                for cls in parent_classes:
                    if isinstance(cls, str) and cls.startswith("highlight"):
                        # highlight 다음에 언어가 올 수 있음
                        parts = cls.split("-")
                        if len(parts) > 1:
                            return parts[-1]

        # 기본값
        return "python"

    def _extract_last_updated(self, soup: BeautifulSoup) -> str | None:
        """문서 수정일 추출."""
        # MkDocs Material의 일반적인 수정일 위치
        last_updated = soup.select_one(".md-source-date, .git-revision-date")
        if last_updated:
            return str(last_updated.get_text(strip=True))
        return None
