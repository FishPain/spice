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
    all_articles = state.get("relevant_articles", [])

    if index + 1 < len(all_articles):
        state["current_index"] = index + 1
        state["current_article"] = all_articles[index + 1]
    else:
        print("✅ All relevant articles processed.")
    return state


def handle_no_articles(state: GraphState) -> GraphState:
    """
    Handles the case where no articles are scraped.
    Sets the response to indicate no articles were found.
    """
    state["response"] = HumanMessage(content="No new articles were found.")
    return state


def collect_relevant_articles(state: GraphState) -> GraphState:
    """
    After scoring all articles, collect only those marked as relevant.
    """
    all_articles = state.get("scraped_data", [])
    all_relevance = state.get("relevance", [])

    relevant_articles = []
    relevant_indices = []

    for i, score in enumerate(all_relevance):
        if score.get("is_relevant", False):
            relevant_articles.append(all_articles[i])
            relevant_indices.append(i)

    # Store only the relevant articles for downstream processing
    state["relevant_articles"] = relevant_articles
    state["relevant_indices"] = relevant_indices
    state["current_index"] = 0
    if relevant_articles:
        state["current_article"] = relevant_articles[0]
    else:
        state["current_article"] = {}

    return state


def build_graph():
    workflow = StateGraph(GraphState)

    # Nodes
    workflow.add_node("web_scrape", web_scrape_handler_node)
    workflow.add_node("score_next", relevance_scoring_node)
    workflow.add_node("collect_relevant", collect_relevant_articles)
    workflow.add_node(
        "business_entity_identification", business_entity_identification_node
    )
    workflow.add_node("opportunity_identification", opportunity_identification_node)
    workflow.add_node("email_outreach", email_outreach_node)
    workflow.add_node("out_of_scope", handle_unrelated_content)
    workflow.add_node("next_article_or_end", next_article_or_end)
    workflow.add_node("handle_no_articles", handle_no_articles)

    # Edges
    workflow.add_edge(START, "web_scrape")

    # If no articles at all
    workflow.add_conditional_edges(
        "web_scrape",
        lambda state: len(state["scraped_data"]) > 0,
        {
            True: "score_next",
            False: "handle_no_articles",
        },
    )

    # Score each article, one-by-one
    workflow.add_conditional_edges(
        "score_next",
        lambda state: state["current_index"] + 1 < len(state["scraped_data"]),
        {
            True: "score_next",  # Continue scoring
            False: "collect_relevant",  # Done scoring
        },
    )

    # If at least 1 relevant article → process
    workflow.add_conditional_edges(
        "collect_relevant",
        lambda state: len(state.get("relevant_articles", [])) > 0,
        {
            True: "business_entity_identification",
            False: "handle_no_articles",
        },
    )

    # Then process each article
    workflow.add_edge("business_entity_identification", "opportunity_identification")
    workflow.add_edge("opportunity_identification", "email_outreach")
    workflow.add_edge("email_outreach", "next_article_or_end")

    # Continue to next relevant
    workflow.add_conditional_edges(
        "next_article_or_end",
        lambda state: state["current_index"] + 1 < len(state["relevant_articles"]),
        {
            True: "business_entity_identification",
            False: END,
        },
    )

    workflow.add_edge("handle_no_articles", END)
    workflow.add_edge("out_of_scope", END)

    return workflow
