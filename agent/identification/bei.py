import logging
from langchain_core.messages import HumanMessage
from agent.templates import BusinessEntity, GraphState, NewsArticle, OpenAI

# Set up logger for this module
logger = logging.getLogger("spice.bei")


def business_entity_identification(
    model: OpenAI, spice_context: str, article: NewsArticle
) -> BusinessEntity:
    """
    Extract the top five most relevant business entities from the article
    for SPICE outreach, returning their name, type, and role.
    """
    prompt = f"""
You are a business entity identification expert for SPICE (SIT-Polytechnic Innovation Centre of Excellence).
Extract up to **5** organizations mentioned in this article that SPICE could collaborate with.
Relevance means the entity plays a major role (leading an initiative, receiving funding/licenses, or partnering).
Do not include government agencies at all. Only include companies that are directly mentioned in the article.
Return JSON with a single key `entities`, a list of objects each having:
- `name`: full organization name
- `type`: "company" or "government agency"
- `role`: its role in the article

### SPICE Context:
{spice_context}

### Article Content:
{article.body}
"""

    parser = model.with_structured_output(BusinessEntity)
    return parser.invoke([HumanMessage(content=prompt)])


def business_entity_identification_node(state: GraphState) -> GraphState:
    """
    For each article marked relevant, run the BEI prompt and keep up to 5 entities.
    """
    logger.info("=" * 80)
    logger.info("BUSINESS ENTITY IDENTIFICATION NODE STARTED")
    logger.info("=" * 80)

    articles = state.get("articles", [])
    relevant_articles = [
        a for a in articles if getattr(a, "relevance", None) and a.relevance.is_relevant
    ]

    logger.info(
        f"Identifying business entities for {len(relevant_articles)} relevant articles"
    )

    for i, article in enumerate(articles, 1):
        if getattr(article, "relevance", None) and article.relevance.is_relevant:
            logger.info(f"[{i}/{len(articles)}] Processing: {article.title[:60]}...")
            try:
                result: BusinessEntity = business_entity_identification(
                    state["model"], state["spice_context"], article
                )
                # Truncate to top 5
                article.business_entities = result.entities[:5]
                logger.info(
                    f"[{i}/{len(articles)}] Found {len(article.business_entities)} entities"
                )
                for entity in article.business_entities:
                    logger.debug(f"  - {entity.name} ({entity.type}): {entity.role}")
            except Exception as e:
                logger.error(
                    f"[{i}/{len(articles)}] Error identifying entities: {e}",
                    exc_info=True,
                )
                article.business_entities = []
        else:
            article.business_entities = []
            logger.debug(
                f"[{i}/{len(articles)}] Skipping (not relevant): {article.title[:60]}..."
            )

    logger.info("✓ Business entity identification completed")
    logger.info("=" * 80)
    return state
