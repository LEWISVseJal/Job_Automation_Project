"""
Resume schemas.

Defines the structured information extracted from a resume.

This structure will later be used by the matching engine.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================
# EDUCATION
# ============================================================

class Education(BaseModel):
    """Education entry."""

    degree: str = ""

    field_of_study: str = ""

    institution: str = ""

    location: Optional[str] = None

    start_date: Optional[str] = None

    end_date: Optional[str] = None

    grade: Optional[str] = None


# ============================================================
# EXPERIENCE
# ============================================================

class Experience(BaseModel):
    """Professional experience entry."""

    job_title: str = ""

    company: str = ""

    location: Optional[str] = None

    start_date: Optional[str] = None

    end_date: Optional[str] = None

    description: str = ""

    responsibilities: List[str] = Field(
        default_factory=list
    )

    technologies: List[str] = Field(
        default_factory=list
    )


# ============================================================
# PROJECT
# ============================================================

class Project(BaseModel):
    """Resume project."""

    name: str = ""

    description: str = ""

    technologies: List[str] = Field(
        default_factory=list
    )

    responsibilities: List[str] = Field(
        default_factory=list
    )

    project_url: Optional[str] = None


# ============================================================
# CERTIFICATION
# ============================================================

class Certification(BaseModel):
    """Certification or professional credential."""

    name: str = ""

    issuing_organization: Optional[str] = None

    issue_date: Optional[str] = None

    expiry_date: Optional[str] = None

    credential_id: Optional[str] = None

    credential_url: Optional[str] = None


# ============================================================
# LANGUAGE
# ============================================================

class Language(BaseModel):
    """Language listed on the resume."""

    name: str = ""

    proficiency: Optional[str] = None


# ============================================================
# RESUME SKILLS
# ============================================================

class ResumeSkills(BaseModel):
    """Categorized resume skills."""

    programming_languages: List[str] = Field(
        default_factory=list
    )

    machine_learning: List[str] = Field(
        default_factory=list
    )

    deep_learning: List[str] = Field(
        default_factory=list
    )

    data_science: List[str] = Field(
        default_factory=list
    )

    databases: List[str] = Field(
        default_factory=list
    )

    frameworks: List[str] = Field(
        default_factory=list
    )

    tools: List[str] = Field(
        default_factory=list
    )

    cloud_and_deployment: List[str] = Field(
        default_factory=list
    )

    other: List[str] = Field(
        default_factory=list
    )


# ============================================================
# COMPLETE RESUME
# ============================================================

class Resume(BaseModel):
    """
    Complete parsed resume structure.

    This represents resume.json.
    """

    name: str = ""

    professional_summary: str = ""

    skills: ResumeSkills = Field(
        default_factory=ResumeSkills
    )

    education: List[Education] = Field(
        default_factory=list
    )

    experience: List[Experience] = Field(
        default_factory=list
    )

    projects: List[Project] = Field(
        default_factory=list
    )

    certifications: List[Certification] = Field(
        default_factory=list
    )

    languages: List[Language] = Field(
        default_factory=list
    )

    total_experience_years: float = 0.0

    resume_file: Optional[str] = None