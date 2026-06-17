"""Generate sample research reports and save to samples/."""

import json
from pathlib import Path

from app.agents.graph import research_graph

TOPICS = [
    ("generative_ai_report.json", "Impact of Generative AI on Software Development"),
    ("renewable_energy_report.json", "Renewable Energy Adoption in Developing Countries"),
]

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"


def main() -> None:
    SAMPLES_DIR.mkdir(exist_ok=True)

    for filename, topic in TOPICS:
        print(f"Generating report for: {topic}")
        result = research_graph.invoke({"topic": topic})

        output = {
            "topic": topic,
            "executive_summary": result.get("executive_summary", ""),
            "key_findings": result.get("key_findings", []),
            "supporting_evidence": result.get("supporting_evidence", []),
            "fact_check_results": result.get("fact_check_results", []),
            "references": result.get("references", []),
            "conclusion": result.get("conclusion", ""),
            "search_providers_used": result.get("search_providers_used", []),
        }

        path = SAMPLES_DIR / filename
        path.write_text(json.dumps(output, indent=2), encoding="utf-8")
        print(f"Saved: {path}")


if __name__ == "__main__":
    main()
