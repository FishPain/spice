from langchain.schema import HumanMessage
from agent.templates import Opportunity


def opportunity_identification_node(state):
    """
    This node identifies opportunities for SPICE to collaborate with the business entity mentioned in the article.
    """
    model = state["model"]
    spice_context = state["spice_context"]
    scraped_data = state["current_article"].get("body")

    prompt = f"""
You are an innovation opportunity analyst working for SPICE (SIT-Polytechnic Innovation Centre of Excellence), a department that supports applied R&D, prototyping, and industry partnerships with local companies and agencies.

Your task is to read the following article and **identify specific areas where SPICE could offer valuable collaboration opportunities** based on its expertise.

Use **step-by-step reasoning** before concluding:
1. Summarize the key issues or initiatives in the article.
2. Identify which of those areas require technical innovation or applied research.
3. Match those needs with SPICE's domain strengths.
4. Conclude with a structured opportunity and justification.

---

### Example Input:
The National Environment Agency (NEA) has issued a licence to Beverage Container Return Scheme Ltd. (BCRS Ltd.) to operate a recycling program using reverse vending machines. The goal is to improve recycling rates of plastic and metal beverage containers. The scheme involves setting up over 1,000 return points and managing logistics and systems to ensure operational efficiency. The project starts in 2026.

### Example Output:
Reasoning:
- The article describes a nationwide infrastructure rollout (reverse vending machines).
- The initiative will require IoT systems, logistics automation, and consumer-facing hardware.
- These needs match SPICE's expertise in IoT, system design, and data analytics.

Response:
{{
  "opportunity": "SPICE can collaborate with BCRS Ltd. to design and prototype the IoT infrastructure, system control logic, and data reporting platform for the return vending network.",
  "justification": "The project aligns with SPICE's strengths in IoT, systems engineering, and smart automation. It also presents a real-world industry use case for SIT students and researchers."
}}

---

### SPICE Context:
{spice_context}

### Article Content:
{scraped_data}
"""
    structured_output_parser = model.with_structured_output(Opportunity)
    decision_response = structured_output_parser.invoke([HumanMessage(content=prompt)])
    if state.get("opportunity", None) is None:
        state["opportunity"] = []
    state["opportunity"].append(decision_response.opportunity)
    if state.get("justification", None) is None:
        state["justification"] = []
    state["justification"].append(decision_response.justification)
    return state
