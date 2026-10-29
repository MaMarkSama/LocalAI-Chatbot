import asyncio

from web_searcher import SearchSource, WebSearcher, format_sources_markdown


class FakeSearcher(WebSearcher):
    async def _plan_queries(self, query):
        return [query, f"{query} official"], 2, 1

    def _search_query_sync(self, query):
        return [
            {"title": "Official result", "href": "https://example.com/report?utm_source=x", "body": query},
            {"title": "Second result", "href": "https://example.org/news", "body": "details"},
        ]

    def _fetch_page_sync(self, source: SearchSource):
        source.excerpt = f"Extracted content from {source.domain}"
        return source


def test_research_deduplicates_urls_and_numbers_sources():
    searcher = FakeSearcher(max_results=5, max_queries=2, fetch_pages=2)
    report = asyncio.run(searcher.research("test query"))
    assert report["status"] == "ok"
    assert len(report["sources"]) == 2
    assert [source["number"] for source in report["sources"]] == [1, 2]
    assert "utm_source" not in report["sources"][0]["url"]
    assert "[Source 1]" in report["context"]

    cached = asyncio.run(searcher.research("test query"))
    assert cached["cached"] is True
    assert cached["planner_prompt_tokens"] == 0


def test_private_urls_are_rejected_and_markdown_is_stable():
    assert WebSearcher._canonical_url("http://127.0.0.1/secret") == ""
    assert WebSearcher._canonical_url("http://user:pass@example.com/secret") == ""
    assert WebSearcher._canonical_url("http://example.com:11434/api/tags") == ""
    assert WebSearcher._canonical_url("https://printer.internal/admin") == ""
    text = format_sources_markdown([
        {"number": 1, "title": "Example", "url": "https://example.com"}
    ])
    assert "[1] [Example](<https://example.com>)" in text
