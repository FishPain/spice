from langchain.schema import HumanMessage
from agent.templates import GraphState, NewsArticle, OpenAI


def email_outreach(model: OpenAI, spice_context: str, article: NewsArticle) -> str:
    """
    This node drafts cold outreach emails to each identified business entity.
    Updates `email_drafts` as a dict mapping entity name -> email text.
    """
    opportunity = article.opportunity.opportunity
    justification = article.opportunity.justification

    emails = {}
    for entity in article.business_entities:
        name = entity.name
        role = entity.role
        entity_type = entity.type

        prompt = f"""
You are a professional outreach email writer working for SPICE (SIT-Polytechnic Innovation Centre of Excellence), a national innovation platform that helps companies co-develop and scale technical solutions through applied R&D.

Write a concise and persuasive **cold outreach email** to initiate contact with the organization **"{name}"**, a {entity_type}, which was identified in the article below.

Your goal is to spark interest in exploring a potential collaboration with SPICE.

Include the following:
- A friendly and professional introduction of SPICE and its mission
- A summary of the article and {name}'s involvement ({role})
- A tailored proposal of how SPICE could collaborate (based on the opportunity below)
- A call to action (CTA) inviting them to a short meeting
- A warm and courteous closing
- Email subject line
- Signature (placeholders are fine)

Use a clear, confident, and helpful tone. Avoid sounding like a mass email.

---

### SPICE Context:
{spice_context}

### Article Content:
{article.body}

### Collaboration Opportunity:
{opportunity}

### Justification:
{justification}

### Output Format:
Subject: [Concise subject line summarizing the intent]

Dear [Recipient’s Name or Organization Name],

[Intro to SPICE and its mission.]

[Summary of article and the organization’s role.]

[Personalized value proposition and how SPICE can contribute.]

[Call to action for a meeting.]

[Warm closing.]

Best regards,  
[Your Name]  
[Your Position]  
SPICE (SIT-Polytechnic Innovation Centre of Excellence)  
[Contact Details]
"""
        response = model.invoke([HumanMessage(content=prompt)])
        emails[name] = response.content
    return emails


def email_outreach_node(state: GraphState) -> GraphState:
    """
    Handles the email outreach node.
    Drafts outreach emails for each identified business entity and updates the state.
    """
    for article in state.get("articles", []):
        if article.relevance.is_relevant:
            article.email_drafts = email_outreach(
                state["model"], state["spice_context"], article
            )
    return state
