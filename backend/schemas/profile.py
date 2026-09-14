"""
Profile schemas.

Defines the structured information used by the job-search system
to understand the candidate's job preferences and basic profile.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================
# CONTACT INFORMATION
# ============================================================

class ContactInfo(BaseModel):
    """Candidate contact information."""

    full_name: str = ""

    email: str = ""

    phone: str = ""

    linkedin_url: Optional[str] = None

    github_url: Optional[str] = None

    portfolio_url: Optional[str] = None


# ============================================================
# JOB PREFERENCES
# ============================================================

class JobPreferences(BaseModel):
    """Preferences used when searching and ranking jobs."""

    target_roles: List[str] = Field(default_factory=list)

    preferred_locations: List[str] = Field(default_factory=list)

    remote_preference: bool = False

    hybrid_preference: bool = False

    onsite_preference: bool = False

    preferred_employment_types: List[str] = Field(
        default_factory=list
    )

    preferred_experience_levels: List[str] = Field(
        default_factory=list
    )

    minimum_match_score: float = 60.0

    prioritize_easy_apply: bool = True


# ============================================================
# PROFESSIONAL PROFILE
# ============================================================

class ProfessionalProfile(BaseModel):
    """General professional information."""

    headline: str = ""

    summary: str = ""

    current_role: Optional[str] = None

    candidate_type: str = ""

    total_experience_years: float = 0.0

    primary_skills: List[str] = Field(
        default_factory=list
    )

    secondary_skills: List[str] = Field(
        default_factory=list
    )


# ============================================================
# COMPLETE PROFILE
# ============================================================

class Profile(BaseModel):
    """
    Complete candidate profile.

    This represents profile.json.
    """

    contact: ContactInfo = Field(
        default_factory=ContactInfo
    )

    professional: ProfessionalProfile = Field(
        default_factory=ProfessionalProfile
    )

    preferences: JobPreferences = Field(
        default_factory=JobPreferences
    )