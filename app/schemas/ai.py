"""
AI Response Schemas

Pydantic schemas for AI-generated career recommendations.
These schemas validate the JSON output from the LLM.
"""

from typing import List

from pydantic import BaseModel, Field


class AIRoadmap(BaseModel):
    """Schema for AI-generated learning roadmap."""
    
    beginner: List[str] = Field(
        ...,
        description="Beginner level steps",
        min_length=1,
    )
    intermediate: List[str] = Field(
        ...,
        description="Intermediate level steps",
        min_length=1,
    )
    advanced: List[str] = Field(
        ...,
        description="Advanced level steps",
        min_length=1,
    )


class AIResources(BaseModel):
    """Schema for AI-generated learning resources."""
    
    books: List[str] = Field(
        ...,
        description="Recommended books",
        min_length=1,
    )
    courses: List[str] = Field(
        ...,
        description="Recommended courses",
        min_length=1,
    )
    youtube_channels: List[str] = Field(
        ...,
        description="Recommended YouTube channels",
        min_length=1,
    )
    websites: List[str] = Field(
        ...,
        description="Recommended websites",
        min_length=1,
    )


class AIRecommendedCareer(BaseModel):
    """Schema for a single AI-recommended career."""
    
    name: str = Field(..., description="Career name")
    match_score: int = Field(
        ...,
        description="Match score (0-100)",
        ge=0,
        le=100,
    )
    reason: str = Field(
        ...,
        description="Explanation for the recommendation",
        min_length=50,
    )
    roadmap: AIRoadmap = Field(..., description="Learning roadmap")
    resources: AIResources = Field(..., description="Learning resources")


class AICareerResponse(BaseModel):
    """
    Schema for the complete AI career recommendation response.
    
    This is the expected output format from the LLM.
    """
    
    personality_summary: str = Field(
        ...,
        description="Summary of the user's personality",
        min_length=100,
    )
    strengths: List[str] = Field(
        ...,
        description="User's key strengths",
        min_length=3,
        max_length=10,
    )
    weaknesses: List[str] = Field(
        ...,
        description="User's areas for improvement",
        min_length=2,
        max_length=5,
    )
    recommended_careers: List[AIRecommendedCareer] = Field(
        ...,
        description="Top 3 recommended careers",
        min_length=3,
        max_length=3,
    )
