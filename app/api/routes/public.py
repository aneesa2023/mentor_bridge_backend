from fastapi import APIRouter
from app.services.mentors import list_mentors, create_mentor, update_mentor, get_mentor_by_id
from app.services.mentees import list_mentees, create_mentee, update_mentee, get_mentee_by_id
from app.models.mentor import MentorProfile, MentorUpdateProfile
from typing import Dict
from app.core.utils import serialize_mongo_doc

router = APIRouter()

@router.get("/mentors")
def get_mentors():
    return [serialize_mongo_doc(m) for m in list_mentors()]

@router.get("/mentees")
def get_mentees():
    return [serialize_mongo_doc(m) for m in list_mentees()]

@router.get("/mentors/{mentor_id}")
def get_mentor_details(mentor_id: str):
    return serialize_mongo_doc(get_mentor_by_id(mentor_id))

@router.get("/mentees/{mentee_id}")
def get_mentees_details(mentee_id: str):
    return serialize_mongo_doc(get_mentee_by_id(mentee_id))

@router.post("/mentors")
def create_new_mentor(mentor: MentorProfile):
    return create_mentor(mentor.dict())

@router.post("/mentees")
def create_new_mentee(mentee: Dict):  # Consider replacing with a Pydantic model later
    return create_mentee(mentee)

@router.put("/mentors/{mentor_id}")
def update_existing_mentor(mentor_id: str, updated: MentorUpdateProfile):
    return update_mentor(mentor_id, updated.dict(exclude_unset=True))

@router.put("/mentees/{mentee_id}")
def update_existing_mentee(mentee_id: str, updated: Dict):  # Consider using a Pydantic model later
    return update_mentee(mentee_id, updated)