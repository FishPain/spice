from typing import List, Literal
from pydantic import BaseModel, Field, HttpUrl
from typing_extensions import TypedDict


class GraphState(TypedDict):
    model: object
    websites: List[str]  # List of websites to scrape
    website_selected: str  # Key of the selected website from the list
    max_results: int  # Maximum number of articles to scrape from the selected website
    spice_context: str
    scraped_data: List[dict]  # List of articles from web_scrape
    scraped_articles: dict  # Dictionary of articles scraped from various websites
    current_index: int  # Index of the current article
    current_article: dict  # Current article being processed
    aggregated_results: List[dict]  # Stores relevance/entity/opportunity per article
    relevance: List[dict]
    business_entity: List[dict]
    opportunity: str
    justification: str
    email_draft: str
    feedback: str


class NewsLink(BaseModel):
    title: str
    url: HttpUrl


class NewsLinkList(BaseModel):
    links: List[NewsLink]


class RelevanceScore(BaseModel):
    """
    Represents the relevance score of a document.
    """

    is_relevant: bool = Field(
        ...,
        description="Whether the document is relevant to the query.",
    )
    reason: str = Field(
        ...,
        description="A brief explanation for the relevance score.",
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
