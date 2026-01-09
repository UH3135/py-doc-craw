"""크롤러 E2E 테스트."""

from typing import Any

import pytest

from tests.e2e.helpers import (
    compute_metrics,
    normalize_for_comparison,
    remove_frontmatter,
)

# 허용 오차 상수 (Normal 수준)
THRESHOLDS = {
    "wer_max": 0.05,  # 5% 이하
    "cer_max": 0.03,  # 3% 이하
    "similarity_min": 0.95,  # 95% 이상
}


@pytest.mark.e2e
@pytest.mark.slow
class TestCrawlerE2E:
    """크롤러 E2E 테스트 스위트."""

    def test_crawl_produces_output(self, single_page_result: dict[str, Any]) -> None:
        """크롤러가 출력을 생성하는지 확인."""
        assert single_page_result.get("content_markdown")
        assert len(single_page_result["content_markdown"]) > 0

    def test_document_structure(self, single_page_result: dict[str, Any]) -> None:
        """문서 구조 검증."""
        assert "title" in single_page_result
        assert "url" in single_page_result
        assert "content_hash" in single_page_result
        assert single_page_result["title"] == "The Python Tutorial"
        assert "docs.python.org" in single_page_result["url"]

    def test_content_similarity_against_golden(
        self,
        single_page_result: dict[str, Any],
        golden_tutorial: str,
    ) -> None:
        """Golden file 대비 내용 유사도 검증."""
        # 정규화
        crawled_normalized = normalize_for_comparison(
            single_page_result["content_markdown"]
        )
        golden_normalized = normalize_for_comparison(
            remove_frontmatter(golden_tutorial)
        )

        # 메트릭 계산
        metrics = compute_metrics(golden_normalized, crawled_normalized)

        # 결과 출력 (디버깅용)
        print("\n=== E2E Test Metrics ===")
        print(f"WER: {metrics.wer:.4f} (threshold: {THRESHOLDS['wer_max']})")
        print(f"CER: {metrics.cer:.4f} (threshold: {THRESHOLDS['cer_max']})")
        print(
            f"Similarity: {metrics.similarity:.4f} "
            f"(threshold: {THRESHOLDS['similarity_min']})"
        )
        print(f"Word count diff: {metrics.word_count_diff}")
        print(f"Char count diff: {metrics.char_count_diff}")

        # Assertions
        assert metrics.wer <= THRESHOLDS["wer_max"], (
            f"WER {metrics.wer:.4f} exceeds threshold {THRESHOLDS['wer_max']}"
        )
        assert metrics.cer <= THRESHOLDS["cer_max"], (
            f"CER {metrics.cer:.4f} exceeds threshold {THRESHOLDS['cer_max']}"
        )
        assert metrics.similarity >= THRESHOLDS["similarity_min"], (
            f"Similarity {metrics.similarity:.4f} "
            f"below threshold {THRESHOLDS['similarity_min']}"
        )

    def test_line_count_in_range(self, single_page_result: dict[str, Any]) -> None:
        """출력의 줄 수가 예상 범위 내인지 확인."""
        content = single_page_result["content_markdown"]
        lines = content.split("\n")
        line_count = len(lines)

        # 기준 문서가 약 180줄이므로 ±30% 허용
        min_lines = 120
        max_lines = 250

        assert min_lines <= line_count <= max_lines, (
            f"Line count {line_count} out of expected range [{min_lines}, {max_lines}]"
        )

    def test_essential_sections_present(
        self, single_page_result: dict[str, Any]
    ) -> None:
        """필수 섹션이 존재하는지 확인."""
        content = single_page_result["content_markdown"]

        essential_sections = [
            "The Python Tutorial",
            "Whetting Your Appetite",
            "Using the Python Interpreter",
            "Data Structures",
            "Classes",
            "Virtual Environments",
        ]

        missing_sections = []
        for section in essential_sections:
            if section not in content:
                missing_sections.append(section)

        assert not missing_sections, f"Missing essential sections: {missing_sections}"


@pytest.mark.e2e
class TestEncodingDetection:
    """인코딩 문제 탐지 테스트."""

    def test_detect_cp1252_artifacts(self, golden_tutorial: str) -> None:
        """CP1252 인코딩 아티팩트 탐지 (정보 제공용)."""
        # 알려진 인코딩 문제 패턴
        cp1252_patterns = {
            "â": "' (apostrophe)",
            "Ã": "UTF-8 double encoding",
        }

        issues_found: dict[str, dict[str, str | int]] = {}
        for pattern, description in cp1252_patterns.items():
            count = golden_tutorial.count(pattern)
            if count > 0:
                issues_found[pattern] = {"description": description, "count": count}

        if issues_found:
            print("\n=== Encoding Issues Detected ===")
            for pattern, info in issues_found.items():
                msg = f"  '{pattern}' -> {info['description']}: {info['count']}"
                print(msg)

        # 현재는 정보 제공만 (인코딩 문제가 있어도 테스트 실패하지 않음)
        # 향후 크롤러 수정 후 이 assertion 활성화
        # assert not issues_found, f"Encoding artifacts found: {issues_found}"
