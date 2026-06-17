import logging
from dataclasses import dataclass

from duckduckgo_search import DDGS
from tavily import TavilyClient

from app.config import get_settings

logger = logging.getLogger(__name__)


class SearchError(Exception):
    def __init__(self, query: str, tavily_error: str, duckduckgo_error: str) -> None:
        self.query = query
        self.tavily_error = tavily_error
        self.duckduckgo_error = duckduckgo_error
        super().__init__(
            f"Search failed for query={query!r}. "
            f"Tavily: {tavily_error}. DuckDuckGo: {duckduckgo_error}."
        )


@dataclass
class SearchResult:
    title: str
    url: str
    content: str
    provider: str


def _tavily_search(query: str, max_results: int) -> list[SearchResult]:
    settings = get_settings()
    if not settings.tavily_api_key:
        raise ValueError("TAVILY_API_KEY is not configured")

    client = TavilyClient(api_key=settings.tavily_api_key)
    response = client.search(query=query, max_results=max_results)

    if not response or "results" not in response:
        raise ValueError("Tavily returned an empty or invalid response")

    results: list[SearchResult] = []
    for item in response["results"]:
        url = item.get("url", "")
        if not url:
            continue
        results.append(
            SearchResult(
                title=item.get("title", ""),
                url=url,
                content=item.get("content", ""),
                provider="tavily",
            )
        )

    if not results:
        raise ValueError("Tavily returned no usable results")

    return results


def _duckduckgo_search(query: str, max_results: int) -> list[SearchResult]:
    raw_results = DDGS().text(query, max_results=max_results)
    if not raw_results:
        raise ValueError("DuckDuckGo returned no results")

    results: list[SearchResult] = []
    for item in raw_results:
        url = item.get("href", "")
        if not url:
            continue
        results.append(
            SearchResult(
                title=item.get("title", ""),
                url=url,
                content=item.get("body", ""),
                provider="duckduckgo",
            )
        )

    if not results:
        raise ValueError("DuckDuckGo returned no usable results")

    return results


def search(query: str, max_results: int = 5) -> list[SearchResult]:
    tavily_error = ""
    try:
        return _tavily_search(query, max_results)
    except Exception as exc:
        tavily_error = str(exc)
        logger.warning(
            "Tavily failed for query=%r: %s — falling back to DuckDuckGo",
            query,
            tavily_error,
        )

    duckduckgo_error = ""
    try:
        return _duckduckgo_search(query, max_results)
    except Exception as exc:
        duckduckgo_error = str(exc)
        logger.error(
            "DuckDuckGo also failed for query=%r: %s",
            query,
            duckduckgo_error,
        )

    raise SearchError(query, tavily_error, duckduckgo_error)


def format_search_results(results: list[SearchResult]) -> str:
    blocks: list[str] = []
    for index, result in enumerate(results, start=1):
        blocks.append(
            f"[{index}] {result.title}\n"
            f"URL: {result.url}\n"
            f"Content: {result.content}\n"
            f"Provider: {result.provider}"
        )
    return "\n\n".join(blocks)
