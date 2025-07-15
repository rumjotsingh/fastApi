from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.schemas.user import UserOut, UserUpdate
from app.db.connection import db

router = APIRouter()

# User routes
@router.get("/me", response_model=UserOut)
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    return {"email": current_user["email"], "name": current_user["name"], "role": current_user["role"]}

@router.put("/me", response_model=UserOut)
async def update_my_profile(update: UserUpdate, current_user: dict = Depends(get_current_user)):
    update_data = {k: v for k, v in update.dict(exclude_unset=True).items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")
    await db["users"].update_one({"email": current_user["email"]}, {"$set": update_data})
    updated = await db["users"].find_one({"email": current_user["email"]})
    return {"email": updated["email"], "name": updated["name"], "role": updated["role"]}

# Admin-only routes
@router.get("/", response_model=list[UserOut])
async def list_users(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    users = await db["users"].find().to_list(100)
    return [{"email": u["email"], "name": u["name"], "role": u["role"]} for u in users]
