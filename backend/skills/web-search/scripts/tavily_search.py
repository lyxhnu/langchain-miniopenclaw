from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import httpx


API_URL = "https://api.tavily.com/search"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a Tavily search and print compact JSON results.")
    parser.add_argument("--query", required=True, help="Search query text.")
    parser.add_argument(
        "--topic",
        choices=("general", "news", "finance"),
        default="general",
        help="Search topic.",
    )
    parser.add_argument(
        "--search-depth",
        choices=("basic", "advanced", "fast", "ultra-fast"),
        default="basic",
        help="Latency vs relevance tradeoff.",
    )
    parser.add_argument("--max-results", type=int, default=5, help="Number of results to request.")
    parser.add_argument(
        "--time-range",
        choices=("day", "week", "month", "year", "d", "w", "m", "y"),
        help="Relative publish/update time filter.",
    )
    parser.add_argument("--start-date", help="Absolute start date in YYYY-MM-DD.")
    parser.add_argument("--end-date", help="Absolute end date in YYYY-MM-DD.")
    parser.add_argument(
        "--include-answer",
        choices=("none", "basic", "advanced"),
        default="none",
        help="Include Tavily's generated answer.",
    )
    parser.add_argument(
        "--include-raw-content",
        choices=("none", "markdown", "text"),
        default="none",
        help="Include extracted page content in each result.",
    )
    parser.add_argument(
        "--include-domain",
        action="append",
        default=[],
        help="Domain to include. Repeat the flag for multiple domains.",
    )
    parser.add_argument(
        "--exclude-domain",
        action="append",
        default=[],
        help="Domain to exclude. Repeat the flag for multiple domains.",
    )
    parser.add_argument("--country", help="Country boost. Only valid for topic=general.")
    parser.add_argument("--auto-parameters", action="store_true", help="Let Tavily infer parameters.")
    parser.add_argument("--include-favicon", action="store_true", help="Include favicon URLs.")
    parser.add_argument("--project-id", help="Optional Tavily project id.")
    parser.add_argument("--timeout", type=float, default=20.0, help="HTTP timeout in seconds.")
    return parser.parse_args()


def compact_text(value: Any, limit: int) -> str:
    text = str(value or "").replace("\u200b", "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def emit_json(payload: dict[str, Any], exit_code: int) -> int:
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    encoding = sys.stdout.encoding or "utf-8"
    sys.stdout.buffer.write(text.encode(encoding, errors="replace"))
    sys.stdout.buffer.flush()
    return exit_code


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "query": args.query,
        "topic": args.topic,
        "search_depth": args.search_depth,
        "max_results": max(0, min(args.max_results, 20)),
    }
    if args.time_range:
        payload["time_range"] = args.time_range
    if args.start_date:
        payload["start_date"] = args.start_date
    if args.end_date:
        payload["end_date"] = args.end_date
    if args.include_answer != "none":
        payload["include_answer"] = args.include_answer
    if args.include_raw_content != "none":
        payload["include_raw_content"] = args.include_raw_content
    if args.include_domain:
        payload["include_domains"] = args.include_domain
    if args.exclude_domain:
        payload["exclude_domains"] = args.exclude_domain
    if args.country:
        payload["country"] = args.country
    if args.auto_parameters:
        payload["auto_parameters"] = True
    if args.include_favicon:
        payload["include_favicon"] = True
    return payload


def build_headers(api_key: str, project_id: str | None) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if project_id:
        headers["X-Project-ID"] = project_id
    return headers


def shape_response(data: dict[str, Any]) -> dict[str, Any]:
    shaped_results: list[dict[str, Any]] = []
    for result in data.get("results", []):
        item = {
            "title": result.get("title"),
            "url": result.get("url"),
            "score": result.get("score"),
            "published_date": result.get("published_date"),
            "content": compact_text(result.get("content"), 900),
        }
        if result.get("raw_content"):
            item["raw_content"] = compact_text(result.get("raw_content"), 1500)
        if result.get("favicon"):
            item["favicon"] = result.get("favicon")
        shaped_results.append(item)

    output: dict[str, Any] = {
        "ok": True,
        "query": data.get("query"),
        "topic": data.get("auto_parameters", {}).get("topic") or data.get("topic"),
        "response_time": data.get("response_time"),
        "request_id": data.get("request_id"),
        "usage": data.get("usage"),
        "results": shaped_results,
    }
    if data.get("answer"):
        output["answer"] = compact_text(data.get("answer"), 1200)
    if data.get("auto_parameters"):
        output["auto_parameters"] = data.get("auto_parameters")
    return output


def main() -> int:
    args = parse_args()
    api_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not api_key:
        return emit_json(
            {
                "ok": False,
                "error": "TAVILY_API_KEY is not set.",
                "hint": "Set TAVILY_API_KEY in backend/.env before using this skill.",
            },
            1,
        )

    payload = build_payload(args)
    headers = build_headers(api_key, args.project_id or os.getenv("TAVILY_PROJECT"))

    try:
        response = httpx.post(API_URL, headers=headers, json=payload, timeout=args.timeout)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        body_preview = compact_text(exc.response.text, 1500)
        return emit_json(
            {
                "ok": False,
                "status_code": exc.response.status_code,
                "error": "Tavily returned an error response.",
                "body": body_preview,
            },
            1,
        )
    except httpx.HTTPError as exc:
        return emit_json(
            {
                "ok": False,
                "error": "HTTP request to Tavily failed.",
                "details": str(exc),
            },
            1,
        )

    data = response.json()
    return emit_json(shape_response(data), 0)


if __name__ == "__main__":
    sys.exit(main())
