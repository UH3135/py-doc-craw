"""E2E 테스트 헬퍼 함수."""

import difflib
import re
from dataclasses import dataclass

import yaml
from jiwer import cer, wer

# === 프론트매터 처리 ===


def remove_frontmatter(content: str) -> str:
    """YAML 프론트매터 제거."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return content


def extract_frontmatter(content: str) -> dict[str, str]:
    """YAML 프론트매터 추출."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            result = yaml.safe_load(parts[1])
            return result if isinstance(result, dict) else {}
    return {}


# === 텍스트 정규화 ===


def normalize_for_comparison(content: str) -> str:
    """비교를 위한 문서 정규화."""
    content = remove_frontmatter(content)

    # 인코딩 아티팩트 정규화 (CP1252 -> UTF-8 변환 문제)
    encoding_fixes = [
        ("\u00e2\u0080\u0099", "'"),
        ("\u00e2\u0080\u0094", "—"),
        ("\u00e2\u0080\u009c", '"'),
        ("\u00e2\u0080\u009d", '"'),
        ("â", "'"),
    ]
    for bad, good in encoding_fixes:
        content = content.replace(bad, good)

    # 공백 정규화
    content = re.sub(r"\s+", " ", content)
    return content.strip()


# === 메트릭 계산 ===


@dataclass
class TextMetrics:
    """텍스트 비교 메트릭 결과."""

    wer: float
    cer: float
    similarity: float
    word_count_diff: int
    char_count_diff: int


def compute_metrics(reference: str, hypothesis: str) -> TextMetrics:
    """WER, CER, 유사도 계산."""
    if not reference and not hypothesis:
        return TextMetrics(0.0, 0.0, 1.0, 0, 0)

    if not reference or not hypothesis:
        return TextMetrics(
            1.0,
            1.0,
            0.0,
            abs(len(reference.split()) - len(hypothesis.split())),
            abs(len(reference) - len(hypothesis)),
        )

    return TextMetrics(
        wer=wer(reference, hypothesis),
        cer=cer(reference, hypothesis),
        similarity=difflib.SequenceMatcher(None, reference, hypothesis).ratio(),
        word_count_diff=abs(len(reference.split()) - len(hypothesis.split())),
        char_count_diff=abs(len(reference) - len(hypothesis)),
    )
