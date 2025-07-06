from typing import List, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain.schema import HumanMessage

from agent.scoring.relevance import relevance_scoring_node
from agent.scraping.webscrape import web_scrape_handler_node
from agent.identification.bei import business_entity_identification_node
from agent.identification.opportunity import opportunity_identification_node
from agent.outreach.email import email_outreach_node
from agent.templates import GraphState


def handle_unrelated_content(state):
    state["response"] = HumanMessage(
        content="The query appears to be out of scope for this system."
    )
    return state


def next_article_or_end(state: GraphState) -> GraphState:
    index = state.get("current_index", 0)
    all_articles = state.get("scraped_data", [])

    if index + 1 < len(all_articles):
        state["current_index"] = index + 1
        state["current_article"] = all_articles[index + 1]
        return state
    else:
        print("✅ All articles processed.")
        return state  # return state as-is if done


def build_graph():
    workflow = StateGraph(GraphState)

    workflow.add_node("web_scrape", web_scrape_handler_node)
    workflow.add_node("relevance_scoring", relevance_scoring_node)
    workflow.add_node(
        "business_entity_identification", business_entity_identification_node
    )
    workflow.add_node("opportunity_identification", opportunity_identification_node)
    workflow.add_node("email_outreach", email_outreach_node)
    workflow.add_node("out_of_scope", handle_unrelated_content)
    workflow.add_node("next_article_or_end", next_article_or_end)

    workflow.add_edge(START, "web_scrape")

    workflow.add_conditional_edges(
        "relevance_scoring",
        lambda state: state["relevance"].get("is_relevant", False),
        {
            True: "business_entity_identification",
            False: "next_article_or_end",
        },
    )

    workflow.add_edge("business_entity_identification", "opportunity_identification")
    workflow.add_edge("opportunity_identification", "next_article_or_end")

    workflow.add_conditional_edges(
        "next_article_or_end",
        lambda state: state["current_index"] + 1 < len(state["scraped_data"]),
        {
            True: "relevance_scoring",
            False: END,
        },
    )

    workflow.add_edge("out_of_scope", END)

    return workflow
