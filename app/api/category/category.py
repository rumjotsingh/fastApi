from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from app.db.connection import db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from app.core.security import get_current_user
from app.utils.transform import mongo_obj_to_dict

router = APIRouter()

# GET /categories - list all categories (public)
@router.get("/", response_model=list[CategoryOut])
async def list_categories():
    categories = await db["categories"].find().to_list(100)
    return [mongo_obj_to_dict(c) for c in categories]

# GET /categories/{category_id} - get single category (public)
@router.get("/{category_id}", response_model=CategoryOut)
async def get_category(category_id: str):
    category = await db["categories"].find_one({"_id": ObjectId(category_id)})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return mongo_obj_to_dict(category)

# POST /categories - create category (admin only)
@router.post("/", response_model=CategoryOut)
async def create_category(data: CategoryCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    new_category = data.dict()
    result = await db["categories"].insert_one(new_category)
    new_category["_id"] = result.inserted_id
    return mongo_obj_to_dict(new_category)

# PUT /categories/{category_id} - update category (admin only)
@router.put("/{category_id}", response_model=CategoryOut)
async def update_category(category_id: str, data: CategoryUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    updates = {k: v for k, v in data.dict().items() if v is not None}
    result = await db["categories"].update_one({"_id": ObjectId(category_id)}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    category = await db["categories"].find_one({"_id": ObjectId(category_id)})
    return mongo_obj_to_dict(category)

# DELETE /categories/{category_id} - delete category (admin only)
@router.delete("/{category_id}")
async def delete_category(category_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    result = await db["categories"].delete_one({"_id": ObjectId(category_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"detail": "Category deleted"}
