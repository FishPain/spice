from langchain.schema import HumanMessage
from agent.templates import RelevanceScore


def relevance_scoring_node(state):
    """
    This node checks if the content is relevant to the query.
    If it is, it sets the state to True and continues to the next node.
    If not, it sets the state to False and goes to the out_of_scope node.
    """
    model = state["model"]
    spice_context = state["spice_context"]
    scraped_data = state["scraped_data"].get("body")

    prompt = f"""
You are an expert relevance evaluator working for SPICE (SIT-Polytechnic Innovation Centre of Excellence), a department that supports industry collaborations in applied R&D and innovation projects.

Your goal is to determine whether the following article is relevant for SPICE to consider reaching out to the organization(s) mentioned, based on SPICE’s domain expertise, capabilities, and mission.

Use the provided context about SPICE to assess:
- Is there a potential opportunity for SPICE to collaborate with the company or agency mentioned?
- Does the article describe any problems, initiatives, or projects that align with SPICE's technical capabilities or research interests?

Respond in the following JSON format:

{{
  "is_relevant": true or false,
  "reason": "A brief explanation for your decision"
}}

### Example Input:
The National Environment Agency (NEA) has issued a licence to Beverage Container Return Scheme Ltd. (BCRS Ltd.) to design and operate a nationwide recycling scheme. The scheme will collect plastic and metal beverage containers using reverse vending machines. BCRS Ltd. is formed by Coca-Cola, F&N, and Pokka.

### Example Output:
{{
  "is_relevant": true,
  "reason": "The article discusses a large-scale recycling initiative involving beverage companies and smart return systems, which aligns with SPICE’s capabilities in IoT, systems design, and sustainability innovation. There is a clear opportunity for collaboration in system prototyping and process optimization."
}}

### SPICE Context:
{spice_context}

### Article Content:
{scraped_data}
"""

    structured_output_parser = model.with_structured_output(RelevanceScore)
    decision_response = structured_output_parser.invoke([HumanMessage(content=prompt)])
    state["relevance"] = {
        "is_relevant": decision_response.is_relevant,
        "reason": decision_response.reason,
    }
    return state
