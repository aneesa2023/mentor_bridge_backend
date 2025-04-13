# app/services/mentees.py
from app.core.database import mentees_collection
from bson import ObjectId
from fastapi import HTTPException

def list_mentees():
    return [{"_id": str(m["_id"]), **m} for m in mentees_collection.find()]

def get_mentee_by_id(mentee_id: str):
    mentee = mentees_collection.find_one({"_id": ObjectId(mentee_id)})
    if not mentee:
        raise HTTPException(status_code=404, detail="Mentee not found")
    mentee["id"] = str(mentee["_id"])
    return mentee

def create_mentee(mentee_data: dict):
    result = mentees_collection.insert_one(mentee_data)
    mentee_data["_id"] = str(result.inserted_id)
    return mentee_data

def update_mentee(mentee_id: str, updated_data: dict):
    result = mentees_collection.update_one(
        {"_id": ObjectId(mentee_id)},
        {"$set": updated_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Mentee not found")
    return {"message": "Mentee updated"}