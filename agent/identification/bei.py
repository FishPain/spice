from langchain.schema import HumanMessage
from agent.templates import BusinessEntity, GraphState, NewsArticle, OpenAI


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
    for article in state.get("articles", []):
        if getattr(article, "relevance", None) and article.relevance.is_relevant:
            result: BusinessEntity = business_entity_identification(
                state["model"], state["spice_context"], article
            )
            # Truncate to top 5
            article.business_entities = result.entities[:5]
        else:
            article.business_entities = []
    return state
