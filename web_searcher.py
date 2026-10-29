"""Agent-style web research with source extraction and citations.

Compatibility is preserved: ``search()`` still returns a formatted string for
LINE, while ``research()`` returns structured sources for Web Chat.
"""
from __future__ import annotations

import asyncio
import copy
import ipaddress
import json
import logging
import os
import re
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Dict, Iterable, List, Optional
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

import httpx

from gemma_app.config import env_bool, env_int

try:  # Current package name (duckduckgo-search was renamed to ddgs).
    from ddgs import DDGS
except ImportError:  # pragma: no cover - compatibility during upgrades
    try:
        from duckduckgo_search import DDGS  # type: ignore
    except ImportError:  # pragma: no cover
        DDGS = None  # type: ignore


logger = logging.getLogger(__name__)
_executor = ThreadPoolExecutor(max_workers=6, thread_name_prefix="web_research")
_TRACKING_KEYS = {
    "fbclid", "gclid", "mc_cid", "mc_eid", "ref", "ref_src", "source",
}


@dataclass
class SearchSource:
    title: str
    url: str
    snippet: str = ""
    excerpt: str = ""
    domain: str = ""
    score: float = 0.0

    def public(self, number: int) -> Dict:
        return {
            "number": number,
            "title": self.title,
            "url": self.url,
            "domain": self.domain,
            "snippet": self.snippet,
        }


class _ReadableHTML(HTMLParser):
    """Small dependency-free visible-text extractor for fetched pages."""

    _ignored = {"script", "style", "svg", "noscript", "nav", "footer", "form"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.title = ""
        self._in_title = False
        self.parts: List[str] = []

    def handle_starttag(self, tag: str, attrs):
        tag = tag.lower()
        if tag in self._ignored:
            self.depth += 1
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        if tag in self._ignored and self.depth:
            self.depth -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str):
        text = re.sub(r"\s+", " ", data).strip()
        if not text:
            return
        if self._in_title:
            self.title = f"{self.title} {text}".strip()
        elif not self.depth and len(text) > 1:
            self.parts.append(text)


class WebSearcher:
    def __init__(
        self,
        max_results: Optional[int] = None,
        max_queries: Optional[int] = None,
        fetch_pages: Optional[int] = None,
    ):
        self.max_results = max_results or env_int("SEARCH_MAX_RESULTS", 8, 3, 20)
        self.max_queries = max_queries or env_int("SEARCH_MAX_QUERIES", 3, 1, 5)
        self.fetch_pages = fetch_pages or env_int("SEARCH_FETCH_PAGES", 5, 0, 10)
        self.max_excerpt_chars = env_int("SEARCH_MAX_EXCERPT_CHARS", 3500, 500, 8000)
        self.max_context_chars = env_int("SEARCH_MAX_CONTEXT_CHARS", 18000, 3000, 40000)
        self.region = os.getenv("SEARCH_REGION", "th-th").strip() or "th-th"
        self.safesearch = os.getenv("SEARCH_SAFESEARCH", "moderate").strip() or "moderate"
        self.plan_with_model = env_bool("SEARCH_QUERY_PLANNER", True)
        self.cache_ttl = env_int("SEARCH_CACHE_TTL_SECONDS", 300, 0, 86400)
        self.cache_max = env_int("SEARCH_CACHE_MAX_ENTRIES", 128, 1, 1000)
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "gemma3:9b")
        self._cache: Dict[str, tuple[float, Dict]] = {}
        self._cache_lock = threading.Lock()

    @staticmethod
    def _tokens(text: str) -> List[str]:
        return [t.lower() for t in re.findall(r"[\w\u0E00-\u0E7F]{2,}", text, re.UNICODE)]

    @staticmethod
    def _canonical_url(url: str) -> str:
        try:
            split = urlsplit(url.strip())
            if split.scheme.lower() not in {"http", "https"} or not split.hostname:
                return ""
            if split.username or split.password or split.port not in {None, 80, 443}:
                return ""
            host = split.hostname.lower().rstrip(".")
            if host in {"localhost", "localhost.localdomain"} or host.endswith((".local", ".internal", ".lan")):
                return ""
            try:
                ip = ipaddress.ip_address(host)
                if not ip.is_global:
                    return ""
            except ValueError:
                pass
            clean_query = [
                (k, v) for k, v in parse_qsl(split.query, keep_blank_values=True)
                if not k.lower().startswith("utm_") and k.lower() not in _TRACKING_KEYS
            ]
            path = split.path or "/"
            if path != "/":
                path = path.rstrip("/")
            return urlunsplit((split.scheme.lower(), split.netloc.lower(), path, urlencode(clean_query), ""))
        except Exception:
            return ""

    @staticmethod
    def _is_public_url(url: str) -> bool:
        canonical = WebSearcher._canonical_url(url)
        if not canonical:
            return False
        host = urlsplit(canonical).hostname
        if not host:
            return False
        try:
            addresses = {item[4][0] for item in socket.getaddrinfo(host, None)}
            return bool(addresses) and all(ipaddress.ip_address(address).is_global for address in addresses)
        except (OSError, ValueError):
            return False

    async def _plan_queries(self, query: str) -> tuple[List[str], int, int]:
        fallback = [query.strip()]
        if not self.plan_with_model or self.max_queries <= 1:
            return fallback, 0, 0
        schema = {
            "type": "object",
            "properties": {
                "queries": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "maxItems": self.max_queries,
                }
            },
            "required": ["queries"],
        }
        prompt = (
            "Create focused web-search queries for the user question. Preserve important names, "
            "dates and constraints. Use Thai and/or English as useful. Return JSON only.\n"
            f"Question: {query}"
        )
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                response = await client.post(f"{self.ollama_url}/api/chat", json={
                    "model": self.ollama_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "format": schema,
                    "options": {"temperature": 0.0, "num_predict": 180, "num_ctx": 1024},
                })
                response.raise_for_status()
                payload = response.json()
            planned = json.loads(payload.get("message", {}).get("content", "{}"))
            candidates = [query.strip()] + [str(q).strip() for q in planned.get("queries", [])]
            unique: List[str] = []
            for candidate in candidates:
                if candidate and candidate.casefold() not in {q.casefold() for q in unique}:
                    unique.append(candidate[:300])
            return (
                unique[: self.max_queries] or fallback,
                int(payload.get("prompt_eval_count", 0) or 0),
                int(payload.get("eval_count", 0) or 0),
            )
        except Exception as exc:
            logger.info("Search query planner fallback: %s", exc)
            return fallback, 0, 0

    def _search_query_sync(self, query: str) -> List[Dict]:
        if DDGS is None:
            raise RuntimeError("Web search dependency is missing. Run: pip install -r requirements.txt")
        with DDGS() as ddgs:
            rows = ddgs.text(
                query,
                region=self.region,
                safesearch=self.safesearch,
                max_results=self.max_results,
            )
            return list(rows or [])

    def _rank(self, query: str, query_results: Iterable[tuple[str, List[Dict]]]) -> List[SearchSource]:
        query_tokens = set(self._tokens(query))
        merged: Dict[str, SearchSource] = {}
        occurrences: Dict[str, int] = {}
        for planned_query, rows in query_results:
            for position, raw in enumerate(rows, 1):
                url = self._canonical_url(str(raw.get("href") or raw.get("url") or ""))
                if not url:
                    continue
                title = re.sub(r"\s+", " ", str(raw.get("title") or "Untitled")).strip()
                snippet = re.sub(r"\s+", " ", str(raw.get("body") or raw.get("description") or "")).strip()
                haystack = f"{title} {snippet}".lower()
                overlap = sum(1 for token in query_tokens if token in haystack)
                score = (self.max_results - position + 1) + overlap * 2.5
                if planned_query.casefold() == query.casefold():
                    score += 1.5
                domain = (urlsplit(url).hostname or "").removeprefix("www.")
                if url in merged:
                    merged[url].score += score * 0.35
                    occurrences[url] = occurrences.get(url, 1) + 1
                    if len(snippet) > len(merged[url].snippet):
                        merged[url].snippet = snippet
                else:
                    merged[url] = SearchSource(title, url, snippet, domain=domain, score=score)
                    occurrences[url] = 1
        for url, source in merged.items():
            source.score += (occurrences[url] - 1) * 3.0

        ranked = sorted(merged.values(), key=lambda item: item.score, reverse=True)
        diverse: List[SearchSource] = []
        per_domain: Dict[str, int] = {}
        for source in ranked:
            if per_domain.get(source.domain, 0) >= 2:
                continue
            diverse.append(source)
            per_domain[source.domain] = per_domain.get(source.domain, 0) + 1
            if len(diverse) >= self.max_results:
                break
        return diverse

    def _fetch_page_sync(self, source: SearchSource) -> SearchSource:
        url = source.url
        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; GemmaAIResearch/2.0)"}
            with httpx.Client(timeout=10.0, headers=headers, follow_redirects=False) as client:
                for _ in range(4):
                    if not self._is_public_url(url):
                        return source
                    with client.stream("GET", url) as response:
                        net_stream = response.extensions.get("network_stream")
                        server_addr = net_stream.get_extra_info("server_addr") if net_stream else None
                        if server_addr and server_addr[0]:
                            try:
                                if not ipaddress.ip_address(server_addr[0]).is_global:
                                    return source
                            except ValueError:
                                return source
                        if response.status_code in {301, 302, 303, 307, 308}:
                            target = response.headers.get("location", "")
                            url = self._canonical_url(urljoin(url, target))
                            continue
                        response.raise_for_status()
                        content_type = response.headers.get("content-type", "").lower()
                        if "text/html" not in content_type and "text/plain" not in content_type:
                            return source
                        chunks: List[bytes] = []
                        size = 0
                        for chunk in response.iter_bytes():
                            size += len(chunk)
                            if size > 2_000_000:
                                break
                            chunks.append(chunk)
                    body = b"".join(chunks).decode(response.encoding or "utf-8", errors="replace")
                    parser = _ReadableHTML()
                    parser.feed(body)
                    text = re.sub(r"\s+", " ", " ".join(parser.parts)).strip()
                    if parser.title and source.title == "Untitled":
                        source.title = parser.title[:300]
                    source.url = self._canonical_url(str(response.url)) or source.url
                    source.domain = (urlsplit(source.url).hostname or source.domain).removeprefix("www.")
                    source.excerpt = text[: self.max_excerpt_chars]
                    return source
        except Exception as exc:
            logger.debug("Could not extract %s: %s", source.url, exc)
        return source

    def _format_context(self, sources: List[SearchSource]) -> str:
        blocks: List[str] = []
        used = 0
        for number, source in enumerate(sources, 1):
            excerpt = source.excerpt or source.snippet
            block = (
                f"[Source {number}] {source.title}\n"
                f"URL: {source.url}\n"
                f"Domain: {source.domain}\n"
                f"Extract: {excerpt}"
            )
            if used + len(block) > self.max_context_chars:
                remaining = self.max_context_chars - used
                if remaining < 300:
                    break
                block = block[:remaining]
            blocks.append(block)
            used += len(block)
        return "\n\n".join(blocks)

    async def research(self, query: str) -> Dict:
        started = time.perf_counter()
        clean_query = re.sub(r"\s+", " ", (query or "")).strip()[:1000]
        if not clean_query:
            return {"query": "", "queries": [], "sources": [], "context": "", "duration_ms": 0, "status": "empty"}

        cache_key = clean_query.casefold()
        if self.cache_ttl:
            with self._cache_lock:
                cached = self._cache.get(cache_key)
                if cached and time.time() - cached[0] <= self.cache_ttl:
                    report = copy.deepcopy(cached[1])
                    report.update({
                        "cached": True,
                        "duration_ms": 0,
                        "planner_prompt_tokens": 0,
                        "planner_completion_tokens": 0,
                    })
                    return report
                if cached:
                    self._cache.pop(cache_key, None)

        queries, planner_in, planner_out = await self._plan_queries(clean_query)
        loop = asyncio.get_running_loop()
        jobs = [loop.run_in_executor(_executor, self._search_query_sync, q) for q in queries]
        raw_results = await asyncio.gather(*jobs, return_exceptions=True)
        successful: List[tuple[str, List[Dict]]] = []
        errors: List[str] = []
        for planned_query, result in zip(queries, raw_results):
            if isinstance(result, Exception):
                errors.append(str(result))
            else:
                successful.append((planned_query, result))

        ranked = self._rank(clean_query, successful)
        fetch_jobs = [
            loop.run_in_executor(_executor, self._fetch_page_sync, source)
            for source in ranked[: self.fetch_pages]
        ]
        if fetch_jobs:
            fetched = await asyncio.gather(*fetch_jobs, return_exceptions=True)
            for index, result in enumerate(fetched):
                if not isinstance(result, Exception):
                    ranked[index] = result

        duration_ms = int((time.perf_counter() - started) * 1000)
        public_sources = [source.public(i) for i, source in enumerate(ranked, 1)]
        status = "ok" if ranked else ("error" if errors else "no_results")
        report = {
            "query": clean_query,
            "queries": queries,
            "sources": public_sources,
            "context": self._format_context(ranked),
            "duration_ms": duration_ms,
            "status": status,
            "errors": errors[:3],
            "planner_prompt_tokens": planner_in,
            "planner_completion_tokens": planner_out,
            "fetched_pages": sum(1 for source in ranked if source.excerpt),
            "cached": False,
        }
        if self.cache_ttl:
            with self._cache_lock:
                if len(self._cache) >= self.cache_max:
                    oldest_key = min(self._cache, key=lambda key: self._cache[key][0])
                    self._cache.pop(oldest_key, None)
                self._cache[cache_key] = (time.time(), copy.deepcopy(report))
        return report

    async def search(self, query: str) -> str:
        report = await self.research(query)
        return report.get("context", "")

    def search_sync(self, query: str) -> str:
        """Legacy helper for callers that are not already inside an event loop."""
        return asyncio.run(self.search(query))


def format_sources_markdown(sources: List[Dict]) -> str:
    if not sources:
        return ""
    lines = ["", "", "### แหล่งอ้างอิง"]
    for source in sources:
        number = int(source.get("number", len(lines)))
        title = str(source.get("title") or source.get("domain") or source.get("url") or "Source")
        url = str(source.get("url") or "")
        if url:
            safe_title = title.replace("[", "\\[").replace("]", "\\]")
            lines.append(f"- [{number}] [{safe_title}](<{url}>)")
    return "\n".join(lines)


web_searcher = WebSearcher()
