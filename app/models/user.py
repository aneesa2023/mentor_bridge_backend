from pydantic import BaseModel, HttpUrl, EmailStr
from typing import List, Optional, Dict

class AvailabilityModel(BaseModel):
    monday: Optional[List[str]]
    tuesday: Optional[List[str]]
    wednesday: Optional[List[str]]
    thursday: Optional[List[str]]
    friday: Optional[List[str]]
    saturday: Optional[List[str]]
    sunday: Optional[List[str]]

class MentorProfile(BaseModel):
    full_name: str
    email: EmailStr
    linkedin_url: Optional[HttpUrl]
    github: Optional[HttpUrl]
    website: Optional[HttpUrl]
    photo_url: Optional[HttpUrl]
    school: Optional[str]
    current_company_role: Optional[str]
    experience_years: str  # e.g., '0-1', '2-3'

    personality_tags: List[str]
    mentoring_style: List[str]
    communication_style: List[str]
    hobbies: List[str]
    languages_spoken: List[str]

    mentee_types_to_help: List[str]
    mentoring_reason: str
    availability: AvailabilityModel

    industries: List[str]
    domains: List[str]
    tech_stack: List[str]
    education_level: str
    past_roles: List[str]

    safe_mode: Optional[bool] = False
    visible_fields: Optional[List[str]] = None

    ai_summary: Optional[str]
    profile_vector: Optional[List[float]]