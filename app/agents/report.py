from pydantic import BaseModel, Field

from app.agents.fact_check import VerifiedClaim
from app.agents.llm import invoke_structured
from app.agents.state import ResearchState


class ReportOutput(BaseModel):
    executive_summary: str
    key_findings: list[str]
    supporting_evidence: list[str]
    fact_check_results: list[VerifiedClaim]
    references: list[str]
    conclusion: str


def report_node(state: ResearchState) -> dict:
    topic = state["topic"]

    output = invoke_structured(
        f"""You are a Report Generation Agent. Create a professional research report on: "{topic}"

Structured Summary:
{state.get("structured_summary", "")}

Main Points:
{state.get("main_points", [])}

Observations:
{state.get("observations", [])}

Verified Facts:
{state.get("verified_facts", [])}

Fact-Check Notes:
{state.get("fact_check_notes", [])}

Overall Confidence Score: {state.get("confidence_score", 0.0)}

Source URLs:
{state.get("source_urls", [])}

Instructions:
- Generate executive summary, key findings, supporting evidence, fact-check results, references, and conclusion.
- Include only URLs from the source list above in references.
- fact_check_results must reflect the verified facts with claim, status, confidence, and notes.
- Write in a clear, professional tone.""",
        ReportOutput,
    )

    return {
        "executive_summary": output.executive_summary,
        "key_findings": output.key_findings,
        "supporting_evidence": output.supporting_evidence,
        "fact_check_results": [
            {
                "claim": item.claim,
                "status": item.status,
                "confidence": item.confidence,
                "notes": item.notes,
            }
            for item in output.fact_check_results
        ],
        "references": output.references,
        "conclusion": output.conclusion,
    }
