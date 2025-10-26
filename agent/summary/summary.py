import logging
from langchain_core.messages import HumanMessage
from agent.templates import GraphState, OpenAI

# Set up logger for this module
logger = logging.getLogger("spice.summary")


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
    logger.info("=" * 80)
    logger.info("SUMMARY NODE STARTED")
    logger.info("=" * 80)

    articles = state.get("articles", [])
    if not articles:
        logger.warning("No articles to summarize")
        state["response"] = "No articles to summarize."
        return state

    logger.info(f"Summarizing {len(articles)} articles")

    for i, article in enumerate(articles, 1):
        logger.info(f"[{i}/{len(articles)}] Summarizing: {article.title[:60]}...")
        try:
            article.body = summary(state["model"], state["spice_context"], article)
            logger.debug(
                f"[{i}/{len(articles)}] Summary length: {len(article.body)} chars"
            )
        except Exception as e:
            logger.error(
                f"[{i}/{len(articles)}] Error summarizing article: {e}", exc_info=True
            )

    logger.info("✓ Summary node completed")
    logger.info("=" * 80)
    return state
