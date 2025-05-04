from typing import List, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain.schema import HumanMessage

from agent.scoring.relevance import relevance_scoring_node
from agent.scraping.webscrape import web_scrape_node
from agent.identification.bei import business_entity_identification_node
from agent.identification.opportunity import opportunity_identification_node
from agent.outreach.email import email_outreach_node

class GraphState(TypedDict):
    """
    Represents the state of our graph.
    """

    model: object
    spice_context: str
    scraped_data: dict
    relevance: dict
    business_entity: List[dict]
    opportunity: str
    justification: str
    email_draft: str
    feedback: str


def handle_unrelated_content(state):
    state["response"] = HumanMessage(
        content="The query appears to be out of scope for this system."
    )
    return state


def build_graph():
    """
    Build the workflow as a graph.
    1. retrieve information from website
    2. ⁠relevance (can sit spice partner with them?)
    3. identify the ⁠⁠target company (any companies that they licensed to, or is it an inter gov agency effort)
    4. ⁠⁠opportunity (what are the problems identified through the article and how spice can come into play.)
    [todo] ⁠5. ⁠retrieve company events (if any)
    [todo] 6. ⁠auto email drafting (auto draft cold email to be sent - requires manual sending)
    """

    workflow = StateGraph(GraphState)

    workflow.add_node("web_scrape", web_scrape_node)
    workflow.add_node("relevance_scoring", relevance_scoring_node)
    workflow.add_node(
        "business_entity_identification", business_entity_identification_node
    )
    workflow.add_node("opportunity_identification", opportunity_identification_node)
    workflow.add_node("email_outreach", email_outreach_node)
    workflow.add_node("out_of_scope", handle_unrelated_content)

    workflow.add_edge(START, "web_scrape")
    workflow.add_edge("web_scrape", "relevance_scoring")

    workflow.add_conditional_edges(
        "relevance_scoring",
        lambda state: state["relevance"].get("is_relevant", False),
        {
            False: "out_of_scope",
            True: "business_entity_identification",
        },
    )
    workflow.add_edge("business_entity_identification", "opportunity_identification")
    workflow.add_edge("opportunity_identification", "email_outreach")
    workflow.add_edge("email_outreach", END)
    workflow.add_edge("out_of_scope", END)
    return workflow
