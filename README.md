# PyDoc-Crawler-MVP

Python 공식 문서 및 주요 프레임워크 문서를 수집하여 LLM 학습이나 RAG(검색 증강 생성)에 활용 가능한 **Clean Markdown** 데이터셋을 구축하는 크롤러입니다.

## 주요 기능

- **다중 문서 엔진 지원**
  - Sphinx 계열: `docs.python.org`, `SQLAlchemy`, `LangChain`, `LangGraph`
  - MkDocs 계열: `FastAPI`

- **효율적인 수집 전략**
  - SitemapSpider 우선 사용
  - Sitemap 부재 시 CrawlSpider를 통한 재귀적 링크 탐색

- **증분 수집 (Incremental Crawling)**
  - `content_hash` 비교를 통한 변경된 문서만 업데이트

- **고품질 Markdown 변환**
  - 코드 블록 언어 정보 보존 (`python`, `bash`, `sql`)
  - Header, Footer, Sidebar 등 노이즈 제거

## 기술 스택

| 구분 | 기술 |
|------|------|
| Language | Python 3.10+ |
| Framework | Scrapy |
| Database | SQLite3 |
| Libraries | pydantic, beautifulsoup4, markdownify |

## 데이터 스키마

**Table:** `documents`

| 필드 | 타입 | 설명 |
|------|------|------|
| id | TEXT (PK) | URL의 MD5 Hash |
| source | TEXT | 문서 출처 (예: 'python', 'fastapi') |
| version | TEXT | 프레임워크 버전 |
| url | TEXT | 원본 문서 URL |
| title | TEXT | 문서 제목 |
| content_markdown | TEXT | 정제된 Markdown 본문 |
| content_hash | TEXT | 본문 SHA256 Hash (변경 감지용) |
| last_updated_at | TEXT | 문서 수정일 |
| crawled_at | DATETIME | 수집 시간 |

## 설치

```bash
# 저장소 클론
git clone https://github.com/your-username/py-doc-craw.git
cd py-doc-craw

# uv 설치 (이미 설치되어 있다면 생략)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 설치 및 가상환경 생성
uv sync
```

## 사용법

```bash
# 전체 문서 크롤링 실행
uv run pydoc-crawler

# 결과물은 data/ 디렉토리에 SQLite DB로 저장됨
```

## 프로젝트 구조

```
py-doc-craw/
├── docs/                   # 프로젝트 문서
├── pydoc_crawler/          # Scrapy 프로젝트
│   ├── spiders/            # 사이트별 스파이더
│   ├── items.py            # Pydantic 데이터 모델
│   ├── pipelines.py        # 데이터 처리 파이프라인
│   └── settings.py         # Scrapy 설정
├── data/                   # SQLite DB 및 출력 파일
├── pyproject.toml          # 프로젝트 설정 및 의존성
├── Makefile                # 실행 자동화
└── README.md
```

## 개발 로드맵

### Phase 1: Skeleton & MVP
- [ ] Scrapy 프로젝트 생성 및 환경 설정
- [ ] Python 공식 문서(Sphinx) 스파이더 구현
- [ ] HTML → Markdown 변환 파이프라인 구현
- [ ] JSONL 파일 저장 및 데이터 품질 검증

### Phase 2: Database Integration
- [ ] SQLite 연동 파이프라인 구현
- [ ] Pydantic 모델 유효성 검증 적용
- [ ] 증분 수집(Upsert) 로직 구현

### Phase 3: Expansion
- [ ] FastAPI(MkDocs) 등 추가 사이트 지원
- [ ] 사이트별 Selector 분기 처리 최적화
- [ ] Makefile 작성

## 라이선스

MIT License
