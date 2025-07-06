from langchain.schema import HumanMessage
from agent.templates import BusinessEntity
from agent.templates import GraphState, NewsArticle, OpenAI


def business_entity_identification(
    model: OpenAI, article: NewsArticle
) -> BusinessEntity:
    """
    This node identifies the business entities mentioned in the scraped data.
    It updates the state with the identified business entities.
    """

    prompt = f"""
You are a business entity identification expert assisting SPICE (SIT-Polytechnic Innovation Centre of Excellence), a department that supports industry collaborations in applied R&D and innovation projects.

Your task is to extract all business entities (e.g. companies, government agencies, joint ventures, or organizations) mentioned in the article below. These may include:
- The company or agency responsible for an initiative
- Organizations granted licenses, funding, or contracts
- Entities collaborating on a project

Respond in the following **JSON format**, where the response is an object containing an "entities" key mapped to a list of business entities.

Each entity must include:
- "name": full organization name
- "type": "company" or "government agency"
- "role": its role in the article context

### Example Input:
The National Environment Agency (NEA) has issued a licence to Beverage Container Return Scheme Ltd. (BCRS Ltd.) to design and operate the beverage container return scheme. BCRS Ltd. is formed by Coca-Cola Singapore Beverages Pte. Ltd., F&N Foods Pte. Ltd., and Pokka Pte. Ltd.

### Example Input:
The Urban Redevelopment Authority (URA) and GovTech have partnered with ST Engineering to launch a pilot program for smart lamp posts across downtown Singapore. These lamp posts will integrate sensors for air quality monitoring, footfall tracking, and emergency alerts. The pilot will run for 18 months starting Q3 2024, and ST Engineering will handle system integration and deployment. URA will evaluate the urban design impacts, while GovTech will provide the data backend infrastructure.

### Example Output:
{{
  "entities": [
    {{
      "name": "Urban Redevelopment Authority",
      "type": "government agency",
      "role": "Coordinating the urban planning aspects of the pilot"
    }},
    {{
      "name": "GovTech",
      "type": "government agency",
      "role": "Providing digital infrastructure and backend data systems"
    }},
    {{
      "name": "ST Engineering",
      "type": "company",
      "role": "System integrator responsible for hardware and deployment"
    }}
  ]
}}

### Article Content:
{article.body}
"""

    structured_output_parser = model.with_structured_output(BusinessEntity)
    response = structured_output_parser.invoke([HumanMessage(content=prompt)])
    return response.entities


def business_entity_identification_node(state: GraphState) -> GraphState:
    """
    Handles the business entity identification node.
    Extracts business entities from the current article and updates the state.
    """
    for article in state.get("articles", []):
        if article.relevance.is_relevant:
            article.business_entities = business_entity_identification(
                state["model"], article
            )

    return state
