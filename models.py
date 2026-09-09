from pydantic import BaseModel, Field, ConfigDict
from typing import List

class ResumeAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    match_score: int = Field(ge=0, le=100, description="Overall match score between resume and job description, from 0 to 100")
    matching_skills: List[str] = Field(description="Skills present in the resume that match the job description")
    missing_skills: List[str] = Field(description="Skills required by the job description but absent from the resume")
    suggestions: List[str] = Field(description="Specific, actionable suggestions to improve the resume for this job description")