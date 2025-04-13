# app/models/mentor.py

from typing import Optional, List
from pydantic import BaseModel

class MentorProfile(BaseModel):  # For POST
    full_name: str
    email: str
    experience_years: int
    personality_tags: List[str]
    communication_style: List[str]
    hobbies: List[str]
    languages_spoken: List[str]
    mentee_types_to_help: List[str]
    mentoring_reason: str
    availability: str
    industries: List[str]
    domains: List[str]
    tech_stack: List[str]
    education_level: str
    past_roles: List[str]

class MentorUpdateProfile(BaseModel):  # For PUT (optional fields)
    full_name: Optional[str] = None
    email: Optional[str] = None
    experience_years: Optional[int] = None
    personality_tags: Optional[List[str]] = None
    communication_style: Optional[List[str]] = None
    hobbies: Optional[List[str]] = None
    languages_spoken: Optional[List[str]] = None
    mentee_types_to_help: Optional[List[str]] = None
    mentoring_reason: Optional[str] = None
    availability: Optional[str] = None
    industries: Optional[List[str]] = None
    domains: Optional[List[str]] = None
    tech_stack: Optional[List[str]] = None
    education_level: Optional[str] = None
    past_roles: Optional[List[str]] = None