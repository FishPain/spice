from langchain.schema import HumanMessage
from agent.templates import RelevanceScore
from agent.templates import GraphState, NewsArticle, OpenAI


def relevance_scoring(
    model: OpenAI, spice_context: str, article: NewsArticle
) -> RelevanceScore:
    """
    This node checks if the content is relevant to the query.
    If it is, it sets the state to True and continues to the next node.
    If not, it sets the state to False and goes to the out_of_scope node.
    """
    prompt = f"""
You are an expert relevance evaluator working for SPICE (SIT-Polytechnic Innovation Centre of Excellence), a department that supports industry collaborations in applied R&D and innovation projects.

Your goal is to determine whether the following article is relevant for SPICE to consider reaching out to the organization(s) mentioned, based on SPICE’s domain expertise, capabilities, and mission.

Use the provided context about SPICE to assess:
- Is there a potential opportunity for SPICE to collaborate with the company or agency mentioned?
- Does the article describe any problems, initiatives, or projects that align with SPICE's technical capabilities or research interests?

Based on SPICE’s mission and domain expertise, decide:

1. **is_relevant**: true/false — should SPICE reach out?
2. **reason**: a short justification.
3. **relevant_domains**: pick from SPICE’s domains.  

Return valid JSON matching the Pydantic model schema.

### SPICE Context:
{spice_context}

### Article Content:
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
