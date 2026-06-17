from pydantic import BaseModel, Field

from app.agents.state import ResearchState
from app.config import get_llm


class SummarizationOutput(BaseModel):
    structured_summary: str = Field(description="Organized summary in logical sections")
    main_points: list[str] = Field(description="Concise main points")
    observations: list[str] = Field(description="Important observations")


def summarization_node(state: ResearchState) -> dict:
    topic = state["topic"]
    llm = get_llm().with_structured_output(SummarizationOutput)

    output = llm.invoke(
        f"""You are a Summarization Agent. Process the research gathered on: "{topic}"

Raw Research Notes:
{state.get("raw_research_notes", "")}

Important Findings:
{state.get("important_findings", [])}

Source URLs:
{state.get("source_urls", [])}

Instructions:
- Remove duplicate information.
- Generate concise summaries organized into logical sections.
- Extract main points and important observations."""
    )

    return {
        "structured_summary": output.structured_summary,
        "main_points": output.main_points,
        "observations": output.observations,
    }
