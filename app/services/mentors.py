# app/services/mentors.py
from app.core.database import mentors_collection
from bson import ObjectId
from fastapi import HTTPException

def list_mentors():
    return [{"_id": str(m["_id"]), **m} for m in mentors_collection.find()]

def get_mentor_by_id(mentor_id: str):
    mentor = mentors_collection.find_one({"_id": ObjectId(mentor_id)})
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    mentor["id"] = str(mentor["_id"])
    return mentor

def create_mentor(mentor_data: dict):
    result = mentors_collection.insert_one(mentor_data)
    mentor_data["_id"] = str(result.inserted_id)
    return mentor_data

def update_mentor(mentor_id: str, updated_data: dict):
    result = mentors_collection.update_one(
        {"_id": ObjectId(mentor_id)},
        {"$set": updated_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Mentor not found")
    return {"message": "Mentor updated"}