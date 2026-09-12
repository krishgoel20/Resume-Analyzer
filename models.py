from pydantic import BaseModel, Field, ConfigDict
from typing import List

class RubricDimension(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dimension: str = Field(description="Name of the rubric dimension, e.g. 'Core Skills'")
    points_awarded: int = Field(ge=0, description="Points awarded for this dimension")
    max_points: int = Field(ge=0, description="Maximum possible points for this dimension")
    explanation: str = Field(description="One or two sentence justification for the points awarded")

class SkillMatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill: str = Field(description="Name of the skill")
    evidence: str = Field(description="The exact phrase or sentence from the resume that demonstrates this skill")

class BulletRewrite(BaseModel):
    model_config = ConfigDict(extra="forbid")

    original: str = Field(description="The original resume bullet or line, quoted verbatim")
    rewritten: str = Field(description="An improved version of the bullet, tailored to better match the job description")
    rationale: str = Field(description="One sentence explaining what changed and why it better matches the job description")

class RewriteVerification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    original: str = Field(description="The original bullet, quoted verbatim, matching a rewrite being checked")
    is_supported: bool = Field(description="True if the rewritten version only contains claims reasonably supported by the original; False if it introduces unsupported claims")
    unsupported_claims: List[str] = Field(description="Specific phrases in the rewrite that are not supported by the original. Empty list if fully supported.")

class ResumeAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    match_score: int = Field(ge=0, le=100, description="Overall match score, equal to the sum of all rubric points_awarded values")
    rubric: List[RubricDimension] = Field(description="Breakdown of the match score across five weighted dimensions: Core Skills (max 40), Experience Level (max 25), Education/Certifications (max 10), Domain Relevance (max 15), Soft Skills (max 10)")
    matching_skills: List[SkillMatch] = Field(description="Skills present in the resume that match the job description, each with a direct quote from the resume as evidence")
    missing_skills: List[str] = Field(description="Skills required by the job description but absent from the resume")
    suggestions: List[str] = Field(description="Specific, actionable suggestions to improve the resume for this job description")
    rewritten_bullets: List[BulletRewrite] = Field(description="Up to 3 of the weakest or most improvable resume bullets, rewritten to better match the job description")

class VerificationBatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    verifications: List[RewriteVerification] = Field(description="One verification result per rewritten bullet checked")