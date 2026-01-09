# 프로젝트 명세서 (PRD): PyDoc-Crawler-MVP

## 1. 개요 (Overview)
* **프로젝트명:** PyDoc-Crawler-MVP
* **목표 (Goal):** Python 공식 문서 및 주요 프레임워크 문서를 수집하여, LLM 학습이나 RAG(검색 증강 생성)에 즉시 활용 가능한 **Clean Markdown** 데이터셋을 구축한다.
* **타겟 사용자:** 개발자 본인 (Developer)
* **작성일:** 2026-01-09

## 2. 핵심 기능 요구사항 (Functional Requirements)

### A. 수집 (Collection)
- [ ] **대상 사이트 및 엔진 분류:**
    - **Sphinx 계열:** `docs.python.org`, `SQLAlchemy`, `LangChain`, `LangGraph`
    - **MkDocs 계열:** `FastAPI`
- [ ] **수집 전략:**
    - `SitemapSpider`를 우선 사용하여 효율성 확보.
    - Sitemap 부재 시 `CrawlSpider`를 통한 재귀적 링크 탐색(Link Following).
- [ ] **증분 수집 (Incremental Crawling):**
    - `content_hash`를 비교하여 변경된 문서만 DB 업데이트 (중복 방지).

### B. 정제 (Processing)
- [ ] **사이트별 파서 분리:** `Spider` 내부에서 도메인별 CSS Selector 분기 처리 (본문 영역 식별).
- [ ] **Markdown 변환 품질 확보:**
    - HTML → Markdown 변환 (`markdownify` 활용).
    - **코드 블록 보존:** `<pre>`, `<code>` 태그 내의 언어 정보(`python`, `bash`, `sql`) 필수 보존.
    - **노이즈 제거:** Header, Footer, Sidebar, 광고 태그, 'Edit this page' 링크 텍스트 제거.

### C. 저장 (Storage)
- [ ] **데이터 저장소:** `SQLite` (단일 파일 DB).
- [ ] **데이터 관리:**
    - 메타데이터와 본문을 하나의 테이블(`documents`)에서 관리.
    - 필요 시 RAG 파이프라인 연동을 위해 Markdown 파일로 Export 기능 고려.

## 3. 기술 사양 (Technical Specifications)
* **Language:** Python 3.10+
* **Framework:** Scrapy
* **Database:** SQLite3 (Python 내장)
* **Libraries:**
    * `pydantic`: 데이터 스키마 정의 및 유효성 검사.
    * `beautifulsoup4`: HTML 정밀 전처리 및 DOM 파싱.
    * `markdownify`: HTML to Markdown 변환.
* **Infra/Deploy:** Local CLI
    * `Makefile` 또는 Shell Script를 통한 실행 자동화.

## 4. 데이터 스키마 (Data Schema)
**Table Name:** `documents`

| Field Name | Type | Description |
| :--- | :--- | :--- |
| **id** | TEXT (PK) | URL의 MD5 Hash 값 (고유 식별자) |
| **source** | TEXT | 문서 출처 (예: 'python', 'fastapi') |
| **version** | TEXT | 프레임워크 버전 (예: '3.12', 'latest') |
| **url** | TEXT | 원본 문서 URL (Unique) |
| **title** | TEXT | 문서 제목 |
| **content_markdown** | TEXT | 정제된 Markdown 본문 |
| **content_hash** | TEXT | 본문 내용의 SHA256 Hash (변경 감지용) |
| **last_updated_at** | TEXT | 문서 내 명시된 수정일 (없을 시 null) |
| **crawled_at** | DATETIME | 실제 수집된 시간 |

## 5. 마일스톤 (Milestones)

### Phase 1: Skeleton & MVP
- [ ] Scrapy 프로젝트 생성 및 환경 설정.
- [ ] Python 공식 문서(Sphinx) 대상 스파이더 구현.
- [ ] HTML → Markdown 변환 파이프라인 구현.
- [ ] 결과물 JSONL 파일 저장 및 데이터 품질(코드블록 등) 육안 검증.

### Phase 2: Database Integration
- [ ] SQLite 연동 파이프라인(`pipelines.py`) 구현.
- [ ] Pydantic 모델을 통한 데이터 유효성 검증 적용.
- [ ] `content_hash` 기반의 증분 수집(Upsert) 로직 구현.

### Phase 3: Expansion (확장)
- [ ] FastAPI(MkDocs) 등 구조가 다른 문서 사이트 추가.
- [ ] 사이트별 Selector 분기 처리 최적화.
- [ ] `Makefile` 작성을 통한 실행 간소화.
