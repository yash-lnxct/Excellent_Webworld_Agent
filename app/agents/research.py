from pydantic import BaseModel, Field

from app.agents.llm import invoke_structured
from app.agents.state import ResearchState
from app.tools.search import format_search_results, search


class SubQueries(BaseModel):
    queries: list[str] = Field(
        description="1-2 focused search queries to broaden research on the topic"
    )


class ResearchOutput(BaseModel):
    raw_research_notes: str = Field(description="Detailed raw research notes")
    source_urls: list[str] = Field(description="Deduplicated list of source URLs")
    important_findings: list[str] = Field(description="Key insights and trends")


def research_node(state: ResearchState) -> dict:
    topic = state["topic"]

    sub_queries = invoke_structured(
        f"Generate 1-2 focused web search queries to research this topic: {topic}",
        SubQueries,
    )

    all_queries = [topic, *sub_queries.queries[:2]]
    seen_urls: set[str] = set()
    all_results = []
    providers_used: list[str] = []

    for query in all_queries:
        results = search(query, max_results=5)
        providers_used.extend(r.provider for r in results)
        for result in results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                all_results.append(result)

    search_context = format_search_results(all_results)

    output = invoke_structured(
        f"""You are a Research Agent. Analyze the following web search results for the topic: "{topic}"

Search Results:
{search_context}

Instructions:
- Extract relevant content and identify key insights and trends.
- Only include URLs that appear in the search results above.
- Provide detailed raw research notes, a deduplicated URL list, and important findings.""",
        ResearchOutput,
    )

    return {
        "raw_research_notes": output.raw_research_notes,
        "source_urls": output.source_urls,
        "important_findings": output.important_findings,
        "search_providers_used": list(set(providers_used)),
    }
