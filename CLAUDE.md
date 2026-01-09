# PyDoc-Crawler 프로젝트 가이드

## 프로젝트 개요

Python 공식 문서 및 주요 프레임워크 문서를 수집하여 LLM/RAG용 Clean Markdown 데이터셋을 구축하는 크롤러입니다.

## 기술 스택

- **Language**: Python 3.12+
- **Framework**: Scrapy
- **Database**: SQLite3
- **Libraries**: pydantic, beautifulsoup4, markdownify

## 프로젝트 구조

```
py-doc-craw/
├── pydoc_crawler/          # Scrapy 프로젝트
│   ├── spiders/            # 사이트별 스파이더
│   ├── items.py            # Pydantic 데이터 모델
│   ├── pipelines.py        # 데이터 처리 파이프라인
│   └── settings.py         # Scrapy 설정
├── data/                   # SQLite DB 및 출력 파일
├── pyproject.toml          # 프로젝트 설정 및 의존성
└── README.md
```

## 개발 환경

### 패키지 관리

uv를 사용합니다.

```bash
# 의존성 설치
uv sync

# 패키지 추가
uv add <package>

# 개발 의존성 추가
uv add --dev <package>

# 실행
uv run <command>
```

### 코드 품질 도구

pre-commit으로 커밋 전 자동 검사를 수행합니다.

```bash
# pre-commit 설치
uv run pre-commit install

# 수동 실행
uv run pre-commit run --all-files
```

**Ruff** - 린터 및 포매터
```bash
# 린트 검사
uv run ruff check .

# 자동 수정
uv run ruff check --fix .

# 포맷팅
uv run ruff format .
```

**mypy** - 타입 검사
```bash
uv run mypy .
```

## 코딩 컨벤션

- ruff 설정을 따름
- 타입 힌트 필수 (mypy strict 모드)
- docstring은 필요한 경우에만 작성

## Git 커밋 규칙

- 커밋 메시지는 **한국어**로 작성
- 변경 내용 요약은 2~3줄로 간결하게

## 주요 명령어

```bash
# 크롤러 실행
uv run pydoc-crawler

# 테스트 실행
uv run pytest

# 린트 + 타입 검사
uv run ruff check . && uv run mypy .
```
