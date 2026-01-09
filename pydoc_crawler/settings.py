"""Scrapy 설정."""

from pathlib import Path
from typing import Any

# 프로젝트 경로
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Scrapy 기본 설정
BOT_NAME = "pydoc_crawler"
SPIDER_MODULES = ["pydoc_crawler.spiders"]
NEWSPIDERS_MODULE = "pydoc_crawler.spiders"

# 크롤링 정책
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 0.5
CONCURRENT_REQUESTS_PER_DOMAIN = 4

# User-Agent 설정
USER_AGENT = "PyDoc-Crawler/0.1 (+https://github.com/pydoc-crawler)"

# 파이프라인 설정
ITEM_PIPELINES: dict[str, int] = {
    "pydoc_crawler.pipelines.ValidationPipeline": 100,
    "pydoc_crawler.pipelines.JsonLinesPipeline": 300,
}

# 피드 내보내기 설정
FEEDS: dict[str, dict[str, Any]] = {
    str(DATA_DIR / "%(name)s_%(time)s.jsonl"): {
        "format": "jsonlines",
        "encoding": "utf-8",
        "overwrite": False,
    },
}

# 로깅 설정
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"

# 요청 설정
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# 캐시 설정 (개발용)
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400  # 24시간
HTTPCACHE_DIR = str(PROJECT_ROOT / ".scrapy_cache")
