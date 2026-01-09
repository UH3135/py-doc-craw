"""pytest 공통 fixtures."""

from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def project_root() -> Path:
    """프로젝트 루트 경로."""
    return Path(__file__).parent.parent


@pytest.fixture
def fixtures_dir() -> Path:
    """테스트 fixtures 디렉토리."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """테스트 출력 디렉토리 (임시)."""
    output = tmp_path / "data"
    output.mkdir(exist_ok=True)
    return output


@pytest.fixture
def golden_tutorial(fixtures_dir: Path) -> str:
    """Python Tutorial golden file 내용."""
    return (fixtures_dir / "python_tutorial.md").read_text(encoding="utf-8")


@pytest.fixture
def crawl_result(
    project_root: Path, output_dir: Path
) -> Generator[dict[str, Any], None, None]:
    """크롤러 실행 및 결과 반환."""
    import sys

    # test_crawl.py를 import하기 위해 경로 추가
    sys.path.insert(0, str(project_root))
    from test_crawl import fetch_and_parse, save_to_file

    url = "https://docs.python.org/3/tutorial/index.html"
    result = fetch_and_parse(url)
    saved_path = save_to_file(result, str(output_dir))

    yield {
        "result": result,
        "saved_path": saved_path,
        "content": Path(saved_path).read_text(encoding="utf-8"),
    }

    # cleanup: sys.path 복원
    sys.path.remove(str(project_root))
