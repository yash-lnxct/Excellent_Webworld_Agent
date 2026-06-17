from typing import TypedDict


class FactCheckResult(TypedDict):
    claim: str
    status: str
    confidence: float
    notes: str


class ResearchState(TypedDict, total=False):
    topic: str
    search_providers_used: list[str]
    raw_research_notes: str
    source_urls: list[str]
    important_findings: list[str]
    structured_summary: str
    main_points: list[str]
    observations: list[str]
    verified_facts: list[FactCheckResult]
    confidence_score: float
    fact_check_notes: list[str]
    executive_summary: str
    key_findings: list[str]
    supporting_evidence: list[str]
    fact_check_results: list[FactCheckResult]
    references: list[str]
    conclusion: str
