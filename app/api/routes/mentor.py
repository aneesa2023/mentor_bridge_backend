from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.services.mongo import db

router = APIRouter()
mentors = db["mentors"]

@router.post("/register-mentor")
async def register_mentor(data: dict, user=Depends(get_current_user)):
    data["auth0_id"] = user["sub"]
    mentors.insert_one(data)
    return {"message": "Mentor registered", "auth0_id": data["auth0_id"]}
