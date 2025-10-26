from typing import List, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage

from agent.scoring.relevance import relevance_scoring_node
from agent.scraping.webscrape import web_scrape_node
from agent.identification.bei import business_entity_identification_node
from agent.identification.opportunity import opportunity_identification_node
from agent.outreach.email import email_outreach_node
from agent.summary.summary import summary_node
from agent.templates import GraphState


def handle_unrelated_content(state):
    state["response"] = HumanMessage(
        content="The query appears to be out of scope for this system."
    )
    return state


def handle_no_articles(state: GraphState) -> GraphState:
    """
    Handles the case where no articles are scraped.
    Sets the response to indicate no articles were found.
    """
    state["response"] = HumanMessage(content="No new articles were found.")
    return state


def handle_no_relevant_articles(state: GraphState) -> GraphState:
    """
    Handles the case where no relevant articles are found after scoring.
    Sets the response to indicate no relevant articles were identified.
    """
    state["response"] = HumanMessage(content="No relevant articles were identified.")
    return state


def build_graph():
    workflow = StateGraph(GraphState)

    # Nodes
    workflow.add_node("web_scrape", web_scrape_node)
    workflow.add_node("summary", summary_node)
    workflow.add_node("relevance_score", relevance_scoring_node)
    workflow.add_node("bei", business_entity_identification_node)
    workflow.add_node("opportunity_identification", opportunity_identification_node)
    workflow.add_node("email_outreach", email_outreach_node)
    workflow.add_node("out_of_scope", handle_unrelated_content)
    workflow.add_node("handle_no_articles", handle_no_articles)
    workflow.add_node("handle_no_relevant_articles", handle_no_relevant_articles)

    workflow.add_edge(START, "web_scrape")

    workflow.add_conditional_edges(
        "web_scrape",
        lambda state: len(state["articles"]) == 0,
        {
            True: "handle_no_articles",
            False: "summary",
        },
    )

    workflow.add_edge("summary", "relevance_score")

    workflow.add_conditional_edges(
        "relevance_score",
        lambda state: any(
            [article.relevance.is_relevant for article in state["articles"]]
        ),
        {
            True: "bei",
            False: "handle_no_relevant_articles",
        },
    )

    workflow.add_edge("bei", "opportunity_identification")
    workflow.add_edge("opportunity_identification", "email_outreach")
    workflow.add_edge("email_outreach", END)
    workflow.add_edge("handle_no_relevant_articles", END)
    workflow.add_edge("handle_no_articles", END)
    workflow.add_edge("out_of_scope", END)

    return workflow
