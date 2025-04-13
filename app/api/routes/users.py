from fastapi import APIRouter, Depends, Request, HTTPException
from app.core.auth import verify_token
import os
from pymongo import MongoClient

router = APIRouter()
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["users"]
users_collection = db["users"]

@router.post("/api/users/init")
async def init_user(request: Request):
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token.")

    token = auth_header.split(" ")[1]
    payload = verify_token(token)

    user_id = payload.get("sub")
    email = payload.get("email")
    name = payload.get("name")
    picture = payload.get("picture")

    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user ID in token.")

    # Check if user exists
    existing_user = users_collection.find_one({"user_id": user_id})
    if existing_user:
        existing_user["_id"] = str(existing_user["_id"])
        return {"message": "User already exists", "user": existing_user}


    user_data = {
    "user_id": user_id,
    "email": email,
    "name": name,
    "picture": picture,
}

    result = users_collection.insert_one(user_data)
    user_data["_id"] = str(result.inserted_id)

    return {"message": "User created", "user": user_data}

