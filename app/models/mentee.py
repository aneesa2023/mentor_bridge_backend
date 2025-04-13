# app/models/mentee.py

from pydantic import BaseModel, EmailStr, HttpUrl
from typing import List, Optional

class MenteeProfile(BaseModel):
    full_name: str
    email: EmailStr
    school: Optional[str] = None
    education_level: Optional[str] = None
    current_goals: List[str]
    areas_of_help: List[str]
    communication_style: Optional[str] = None
    tech_interests: Optional[List[str]] = []
    personal_description: Optional[str] = None
    languages_spoken: Optional[List[str]] = []
    profile_picture: Optional[HttpUrl] = None
