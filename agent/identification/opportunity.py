from langchain.schema import HumanMessage
from agent.templates import Opportunity
from agent.templates import GraphState, NewsArticle, OpenAI
from agent.context.spice import SPECIALIZED_CONTEXTS
from typing import Dict


def opportunity_identification(
    model: OpenAI,
    spice_context: str,
    filtered_contexts: Dict[str, str],
    article: NewsArticle,
) -> Opportunity:
    """
    This node identifies opportunities for SPICE to collaborate based
    on the article and the filtered specialized contexts.
    """

    # Format the filtered domains as markdown sections
    if filtered_contexts:
        domains_md = "\n\n".join(
            f"### {domain}\n\n{text.strip()}"
            for domain, text in filtered_contexts.items()
        )
    else:
        domains_md = "*(No specialized domains flagged for this article)*"

    prompt = f"""
You are an innovation opportunity analyst for SPICE (SIT-Polytechnic Innovation Centre of Excellence), tasked with identifying how SPICE’s unique technical strengths can address real-world problems described in news articles.

Below you have:

1 **Core SPICE Mission & Capabilities**:  
{spice_context}

2 **Filtered SPICE Expertise** (only domains relevant to this article):  
{domains_md}

3 **Article Title:**  
{article.title}

4 **Article Content:**  
{article.body}

—

**Your step-by-step reasoning** should cover:  
a) Key challenges or initiatives from the article.  
b) Technical innovation or applied research needs implied.  
c) Matching those needs to SPICE’s domains above.  

Finally, **output** a JSON object matching this Pydantic schema for `Opportunity` (no extra keys):

{Opportunity.model_json_schema()}

Your JSON must be valid.  
"""

    parser = model.with_structured_output(Opportunity)
    return parser.invoke([HumanMessage(content=prompt)])


def opportunity_identification_node(state: GraphState) -> GraphState:
    """
    Applies opportunity_identification to each relevant article.
    """
    for article in state.get("articles", []):
        if getattr(article, "relevance", None) and article.relevance.is_relevant:
            domains = article.relevance.relevant_domains or []
            filtered_contexts = {
                key: SPECIALIZED_CONTEXTS[key]
                for key in domains
                if key in SPECIALIZED_CONTEXTS
            }
            article.opportunity = opportunity_identification(
                state["model"],
                state["spice_context"],
                filtered_contexts,
                article,
            )
    return state
