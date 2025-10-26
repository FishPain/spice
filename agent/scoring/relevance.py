from langchain.schema import HumanMessage
from agent.templates import RelevanceScore
from agent.templates import GraphState, NewsArticle, OpenAI


def relevance_scoring(
    model: OpenAI, spice_context: str, article: NewsArticle
) -> RelevanceScore:
    """
    This node checks relevance ONLY if there is clear potential funding
    and/or collaboration with private companies (not government-only news).
    """
    prompt = f"""
You are an expert relevance evaluator for SPICE (SIT-Polytechnic Innovation Centre of Excellence).

Evaluate the article **ONLY** on whether it signals a near- to mid-term opportunity for SPICE to:
- **Receive or access funds** (e.g., grants, corporate R&D funding, venture funding, investment rounds tied to R&D, funded pilots, sponsored projects, procurement with budget),
- **Collaborate with private companies** (e.g., partnerships, MoUs, joint development, paid pilots, RFPs/RFIs from companies, consortiums with corporate members).

Deprioritize / mark **not relevant** if:
- It’s **government-only** (policy, ministry announcements, public programs) **without** a specific private company partnership or funded call SPICE could join.
- It’s generic PR, hiring news, awards, or leadership changes with **no funding** or **no concrete company collaboration path**.
- It’s far-future or speculative with no actionable funding/collab angle.

When **relevant**, briefly point to the company(ies), the funding/collab mechanism, and why it fits SPICE’s capabilities.

Return valid JSON per the Pydantic schema with:
1. "is_relevant": true/false
2. "reason": one short sentence
3. "relevant_domains": pick from SPICE’s domains, only if relevant

### SPICE Context
{spice_context}

### Article Content
{article.body}
"""
    structured_output_parser = model.with_structured_output(RelevanceScore)
    decision_response = structured_output_parser.invoke([HumanMessage(content=prompt)])
    return decision_response


def relevance_scoring_node(state: GraphState) -> GraphState:
    """
    Handles the relevance scoring node.
    If the article is relevant, it continues to the next node.
    If not, it goes to the out_of_scope node.
    """
    articles = state.get("articles", [])
    for article in articles:
        article.relevance = relevance_scoring(
            state["model"], state["spice_context"], article
        )
    return state
