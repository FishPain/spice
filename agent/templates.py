from typing import List, Literal
from pydantic import BaseModel, Field, HttpUrl
from typing_extensions import TypedDict

from langchain_openai import OpenAI
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, HttpUrl
from agent.context.spice import SPECIALIZED_CONTEXTS
from enum import Enum


class NewsLink(BaseModel):
    title: str
    url: HttpUrl


class NewsLinkList(BaseModel):
    links: List[NewsLink]


class RelevanceScore(BaseModel):
    is_relevant: bool = Field(..., description="Whether the article is relevant.")
    reason: str = Field(..., description="Brief explanation for your decision.")
    relevant_domains: List[str] = Field(
        default_factory=list,
        description=(
            "Which of SPICE’s domains apply to this article? "
            "Choose zero or more from: " + ", ".join(SPECIALIZED_CONTEXTS.keys())
        ),
    )


class BusinessEntityItem(BaseModel):
    name: str = Field(..., description="The name of the business entity.")
    type: Literal["company", "government agency"] = Field(
        ..., description="The type of the business entity."
    )
    role: str = Field(
        ...,
        description="The role or involvement of the business entity in the article.",
    )


class BusinessEntity(BaseModel):
    entities: List[BusinessEntityItem] = Field(
        ..., description="List of business entities mentioned in the article."
    )


class Opportunity(BaseModel):
    """
    Represents an opportunity identified in the document.
    """

    opportunity: str = Field(
        ...,
        description="The identified opportunity for SPICE.",
    )
    justification: str = Field(
        ...,
        description="The justification for the identified opportunity.",
    )


class EmailDraft(BaseModel):
    """
    Represents a draft email for outreach.
    """

    subject: str = Field(
        ...,
        description="The subject of the email.",
    )
    body: str = Field(
        ...,
        description="The body content of the email.",
    )
    recipient: str = Field(
        ...,
        description="The recipient of the email.",
    )


class NewsArticle(BaseModel):
    host: str
    title: str
    url: str
    body: Optional[str] = None
    relevance: RelevanceScore = None
    business_entities: List[BusinessEntityItem] = []
    opportunity: Opportunity = None
    email_drafts: List[dict[str, str]] = None


class GraphState(TypedDict):
    model: OpenAI
    spice_context: str
    websites: dict
    website_selected: str
    max_results: int
    articles: List[NewsArticle]
    current_index: int
    current_article: Optional[NewsArticle]
    scraped_articles: dict
    response: Optional[object]
    headless: bool
    browser: Literal["chromium", "firefox", "webkit"]
