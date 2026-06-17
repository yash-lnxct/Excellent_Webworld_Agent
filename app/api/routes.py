from fastapi import APIRouter, HTTPException

from app.agents.graph import research_graph
from app.api.schemas import FactCheckResultSchema, ResearchRequest, ResearchResponse
from app.tools.search import SearchError

router = APIRouter(prefix="/api/v1")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/research", response_model=ResearchResponse)
def create_research_report(request: ResearchRequest) -> ResearchResponse:
    try:
        result = research_graph.invoke({"topic": request.topic})
    except SearchError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    fact_check_results = [
        FactCheckResultSchema(
            claim=item["claim"],
            status=item["status"],
            confidence=item["confidence"],
            notes=item["notes"],
        )
        for item in result.get("fact_check_results", [])
    ]

    return ResearchResponse(
        topic=request.topic,
        executive_summary=result.get("executive_summary", ""),
        key_findings=result.get("key_findings", []),
        supporting_evidence=result.get("supporting_evidence", []),
        fact_check_results=fact_check_results,
        references=result.get("references", []),
        conclusion=result.get("conclusion", ""),
        search_providers_used=result.get("search_providers_used", []),
    )
