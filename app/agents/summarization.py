from pydantic import BaseModel, Field

from app.agents.llm import invoke_structured
from app.agents.state import ResearchState


class SummarizationOutput(BaseModel):
    structured_summary: str = Field(description="Organized summary in logical sections")
    main_points: list[str] = Field(description="Concise main points")
    observations: list[str] = Field(description="Important observations")


def summarization_node(state: ResearchState) -> dict:
    topic = state["topic"]

    output = invoke_structured(
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
- Extract main points and important observations.""",
        SummarizationOutput,
    )

    return {
        "structured_summary": output.structured_summary,
        "main_points": output.main_points,
        "observations": output.observations,
    }
