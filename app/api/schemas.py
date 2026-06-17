from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    topic: str = Field(min_length=3, description="Research topic to investigate")


class FactCheckResultSchema(BaseModel):
    claim: str
    status: str
    confidence: float = Field(ge=0.0, le=1.0)
    notes: str


class ResearchResponse(BaseModel):
    topic: str
    executive_summary: str
    key_findings: list[str]
    supporting_evidence: list[str]
    fact_check_results: list[FactCheckResultSchema]
    references: list[str]
    conclusion: str
    search_providers_used: list[str] = []
