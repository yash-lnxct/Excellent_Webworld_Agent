from langgraph.graph import END, StateGraph

from app.agents.fact_check import fact_check_node
from app.agents.report import report_node
from app.agents.research import research_node
from app.agents.state import ResearchState
from app.agents.summarization import summarization_node


def build_research_graph():
    graph = StateGraph(ResearchState)
    graph.add_node("research", research_node)
    graph.add_node("summarization", summarization_node)
    graph.add_node("fact_check", fact_check_node)
    graph.add_node("report", report_node)
    graph.set_entry_point("research")
    graph.add_edge("research", "summarization")
    graph.add_edge("summarization", "fact_check")
    graph.add_edge("fact_check", "report")
    graph.add_edge("report", END)
    return graph.compile()


research_graph = build_research_graph()
