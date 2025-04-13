# app/api/routes/protected.py
from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.services.users import get_user_profile, update_user_profile

router = APIRouter()

@router.get("/me")
def get_my_profile(user: dict = Depends(get_current_user)):
    return get_user_profile(user["sub"])

@router.post("/me/update")
def update_my_profile(data: dict, user: dict = Depends(get_current_user)):
    return update_user_profile(user["sub"], data)