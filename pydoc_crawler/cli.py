"""CLI 엔트리포인트."""

import argparse
import sys
from typing import NoReturn

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def main() -> NoReturn:
    """크롤러 CLI 메인 함수."""
    parser = argparse.ArgumentParser(
        description="PyDoc Crawler - Python/FastAPI 문서 크롤러",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "spider",
        nargs="?",
        default="python",
        choices=["python", "fastapi"],
        help="실행할 스파이더 이름 (기본값: python)",
    )

    parser.add_argument(
        "-v",
        "--version",
        default="3.13",
        help="Python 문서 버전 (기본값: 3.13)",
    )

    parser.add_argument(
        "--all-versions",
        action="store_true",
        help="지원하는 모든 버전 크롤링 (3.10~3.13)",
    )

    parser.add_argument(
        "--lang",
        default="en",
        help="FastAPI 문서 언어 (기본값: en)",
    )

    parser.add_argument(
        "--section",
        default="tutorial",
        help="수집할 섹션 (기본값: tutorial)",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="출력 파일 경로 (기본값: data/<spider>_output.jsonl)",
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="로그 레벨 (기본값: INFO)",
    )

    args = parser.parse_args()

    # Scrapy 설정 로드
    settings = get_project_settings()
    settings.set("LOG_LEVEL", args.log_level)

    if args.output:
        settings.set(
            "FEEDS",
            {
                args.output: {
                    "format": "jsonlines",
                    "encoding": "utf-8",
                    "overwrite": True,
                }
            },
        )

    # 크롤러 실행
    process = CrawlerProcess(settings)

    if args.spider == "python":
        if args.all_versions:
            versions = ["3.10", "3.11", "3.12", "3.13"]
            for version in versions:
                process.crawl(args.spider, version=version, section=args.section)
        else:
            process.crawl(args.spider, version=args.version, section=args.section)
    elif args.spider == "fastapi":
        process.crawl(args.spider, lang=args.lang, section=args.section)

    process.start()
    sys.exit(0)


if __name__ == "__main__":
    main()
