from fastapi import APIRouter, HTTPException, status
from app.schemas.user import UserCreate, UserOut, Token,UserLogin,TokenWithUser
from app.db.connection import db
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=UserOut)
async def register(user: UserCreate):
    existing = await db["users"].find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash_password(user.password)
    new_user = {"email": user.email, "hashed_password": hashed_pwd, "name": user.name, "role": user.role or "user"}
    await db["users"].insert_one(new_user)

    return UserOut(email=user.email, name=user.name, role=new_user["role"])

@router.post("/login", response_model=TokenWithUser)
async def login(user: UserLogin):
    existing = await db["users"].find_one({"email": user.email})
    if not existing:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(user.password, existing["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": user.email})

    user_profile = UserProfile(
        email=existing["email"],
        name=existing["name"],
        role=existing.get("role", "user")
    )

    return TokenWithUser(access_token=token, user=user_profile)
