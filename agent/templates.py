from typing import List, Literal
from pydantic import BaseModel, Field, RootModel


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
