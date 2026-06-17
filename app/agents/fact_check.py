from pydantic import BaseModel, Field

from app.agents.state import FactCheckResult, ResearchState
from app.config import get_llm
from app.tools.search import format_search_results, search


class ClaimsOutput(BaseModel):
    claims: list[str] = Field(description="5-8 verifiable factual claims from the research")


class VerifiedClaim(BaseModel):
    claim: str
    status: str = Field(description="One of: verified, disputed, unsupported")
    confidence: float = Field(ge=0.0, le=1.0)
    notes: str


class FactCheckOutput(BaseModel):
    verified_facts: list[VerifiedClaim]
    confidence_score: float = Field(ge=0.0, le=1.0)
    fact_check_notes: list[str]


def fact_check_node(state: ResearchState) -> dict:
    topic = state["topic"]
    llm = get_llm()

    claims_llm = llm.with_structured_output(ClaimsOutput)
    claims_output = claims_llm.invoke(
        f"""Extract 5-8 verifiable factual claims from this research on "{topic}":

Findings: {state.get("important_findings", [])}
Summary: {state.get("structured_summary", "")}

Return specific, checkable claims only."""
    )

    cross_ref_blocks: list[str] = []
    providers_used: list[str] = state.get("search_providers_used", [])

    for claim in claims_output.claims[:8]:
        results = search(f"{claim} fact check", max_results=3)
        providers_used.extend(r.provider for r in results)
        cross_ref_blocks.append(
            f"Claim: {claim}\nCross-reference results:\n{format_search_results(results)}"
        )

    fact_check_llm = llm.with_structured_output(FactCheckOutput)
    output = fact_check_llm.invoke(
        f"""You are a Fact-Checking Agent for research on: "{topic}"

Original Findings:
{state.get("important_findings", [])}

Claims to verify:
{claims_output.claims}

Cross-reference search results:
{chr(10).join(cross_ref_blocks)}

Instructions:
- Validate each claim against cross-reference sources.
- Assign status: verified, disputed, or unsupported.
- Provide a confidence score (0-1) per claim and an overall confidence_score.
- Flag unsupported statements in fact_check_notes."""
    )

    verified_facts: list[FactCheckResult] = [
        {
            "claim": item.claim,
            "status": item.status,
            "confidence": item.confidence,
            "notes": item.notes,
        }
        for item in output.verified_facts
    ]

    return {
        "verified_facts": verified_facts,
        "confidence_score": output.confidence_score,
        "fact_check_notes": output.fact_check_notes,
        "search_providers_used": list(set(providers_used)),
    }
