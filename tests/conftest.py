"""pytest 공통 fixtures."""

from pathlib import Path

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
