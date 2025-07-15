from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from app.db.connection import db
from app.schemas.review import ReviewCreate, ReviewOut
from app.core.security import get_current_user

router = APIRouter()

# POST /products/{product_id}/reviews/ - add review
@router.post("/products/{product_id}/reviews/", response_model=ReviewOut)
async def add_review(product_id: str, data: ReviewCreate, current_user: dict = Depends(get_current_user)):
    # Check if product exists
    product = await db["products"].find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    new_review = {
        "rating": data.rating,
        "comment": data.comment,
        "user_id": str(current_user["_id"]),
        "product_id": product_id
    }
    result = await db["reviews"].insert_one(new_review)
    new_review["id"] = str(result.inserted_id)
    return new_review

# GET /products/{product_id}/reviews/ - list reviews
@router.get("/products/{product_id}/reviews/", response_model=list[ReviewOut])
async def list_reviews(product_id: str):
    reviews = []
    async for r in db["reviews"].find({"product_id": product_id}):
        r["id"] = str(r["_id"])
        r.pop("_id", None)
        reviews.append(r)
    return reviews
