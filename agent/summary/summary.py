from langchain_core.messages import HumanMessage
from agent.templates import GraphState, OpenAI


def summary(
    model: OpenAI,
    spice_context: str,
    article: dict,
) -> str:
    """
    Generate a focused summary of the given article that:
      - Captures all the business entities and their roles
      - Preserves any identified collaboration opportunities
      - Keeps any other key technical or project details

    Returns the summary as a plain string.
    """
    prompt = f"""
You are an expert summarizer for SPICE (SIT-Polytechnic Innovation Centre of Excellence).  I will give you one news article.  
Produce a concise (~150 - 250 words) summary that:

  • Mentions every business entity and its role  
  • Describes any collaboration opportunities identified  
  • Includes all major technical initiatives, project goals, or findings  
  • Uses an objective, professional tone  

### SPICE Context
{spice_context}

### Article Title
{article.title}

### Full Text
{article.body}

Please write the summary below:
"""
    resp = model.invoke([HumanMessage(content=prompt)])
    return resp.content.strip()


def summary_node(state: GraphState) -> GraphState:
    """
    Runs through each article in state["articles"] and attaches a
    focused summary at article.summary, without dropping the full body.
    """
    articles = state.get("articles", [])
    if not articles:
        state["response"] = "No articles to summarize."
        return state

    for article in articles:
        article.body = summary(state["model"], state["spice_context"], article)

    return state
