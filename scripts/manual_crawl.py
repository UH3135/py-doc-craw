"""Python 공식 문서 크롤링 테스트."""

import hashlib

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md


def fetch_and_parse(url: str) -> dict[str, str]:
    """URL에서 문서를 가져와 Markdown으로 변환."""
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # 제목 추출 (headerlink 제거)
    title_tag = soup.find("h1")
    if title_tag:
        for link in title_tag.select(".headerlink"):
            link.decompose()
        title = title_tag.get_text(strip=True)
    else:
        title = "Untitled"

    # 본문 영역 추출 (Sphinx 문서 구조)
    content_div = soup.select_one("div.body") or soup.select_one("main")

    if not content_div:
        raise ValueError("본문 영역을 찾을 수 없습니다.")

    # 노이즈 제거
    noise_selectors = [
        "nav",
        ".headerlink",  # 섹션 링크 (¶)
        ".navigation",
        ".footer",
        "script",
        "style",
    ]
    for selector in noise_selectors:
        for element in content_div.select(selector):
            element.decompose()

    # HTML -> Markdown 변환
    markdown_content = md(
        str(content_div),
        heading_style="ATX",
        code_language_callback=lambda el: el.get("data-language", "python"),
    )

    # content hash 생성
    content_hash = hashlib.sha256(markdown_content.encode()).hexdigest()

    return {
        "url": url,
        "title": title,
        "content_markdown": markdown_content.strip(),
        "content_hash": content_hash,
    }


def save_to_file(result: dict[str, str], output_dir: str = "data") -> str:
    """결과를 Markdown 파일로 저장."""
    from pathlib import Path

    # data 폴더 생성
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # 파일명 생성 (URL에서 추출)
    url_hash = result["content_hash"][:8]
    safe_title = result["title"].replace(" ", "_").replace("/", "-")[:50]
    filename = f"{safe_title}_{url_hash}.md"

    filepath = output_path / filename

    # 메타데이터 + 본문 저장
    content = f"""---
title: {result["title"]}
url: {result["url"]}
content_hash: {result["content_hash"]}
---

{result["content_markdown"]}
"""

    filepath.write_text(content, encoding="utf-8")
    return str(filepath)


if __name__ == "__main__":
    test_url = "https://docs.python.org/3/tutorial/index.html"

    print(f"크롤링 중: {test_url}\n")

    result = fetch_and_parse(test_url)

    print(f"제목: {result['title']}")
    print(f"Hash: {result['content_hash'][:16]}...")

    # 파일 저장
    saved_path = save_to_file(result)
    print(f"저장 완료: {saved_path}")
    print(f"총 길이: {len(result['content_markdown'])} 문자")
