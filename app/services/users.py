# app/services/users.py
from app.core.database import users_collection
from bson import ObjectId
from fastapi import HTTPException

def get_user_profile(user_id: str):
    user = users_collection.find_one({"user_id": user_id})
    if user:
        user["_id"] = str(user["_id"])
        return user
    raise HTTPException(status_code=404, detail="User not found")

def update_user_profile(user_id: str, update_data: dict):
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": update_data},
        upsert=True
    )
    return {"message": "Profile updated"}