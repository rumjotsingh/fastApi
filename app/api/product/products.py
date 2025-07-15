# app/api/products.py

from fastapi import APIRouter, HTTPException, Depends, status,Query
from typing import List,Optional
from app.schemas.products import ProductCreate, ProductUpdate, ProductOut
from app.core.security import get_current_user   # your JWT auth dependency
from bson import ObjectId
from app.db.connection import db

# assume db is your Mongo client (e.g., db = client["ecommerce"])

router = APIRouter()

# Helper: check admin
def require_admin(user):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user

@router.post("/", response_model=ProductOut, status_code=201)
async def create_product(product: ProductCreate, user=Depends(get_current_user)):
    require_admin(user)
    new_product = product.dict()
    if "image" in new_product and new_product["image"] is not None:
        new_product["image"] = str(new_product["image"])
    result = await db["products"].insert_one(new_product)
    new_product["id"] = str(result.inserted_id)
    return new_product

@router.get("/", response_model=List[ProductOut])
async def list_products(
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    category: Optional[str] = None
):
    filters = {}

    # Filter by category
    if category:
        filters["category"] = category

    # Filter by price range
    if min_price is not None or max_price is not None:
        price_filter = {}
        if min_price is not None:
            price_filter["$gte"] = min_price
        if max_price is not None:
            price_filter["$lte"] = max_price
        filters["price"] = price_filter

    products = []
    async for p in db["products"].find(filters):
        if p.get("name") is None or p.get("stock") is None:
            continue  # skip invalid products
        p["id"] = str(p["_id"])
        p.pop("_id", None)
        products.append(p)
    return products

@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: str):
    product = await db["products"].find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.get("name") is None or product.get("stock") is None:
        raise HTTPException(status_code=500, detail="Product missing required fields")
    product["id"] = str(product["_id"])
    product.pop("_id", None)
    return product

@router.put("/{product_id}", response_model=ProductOut)
async def update_product(product_id: str, product: ProductUpdate, user=Depends(get_current_user)):
    require_admin(user)
    update_data = {k: v for k, v in product.dict(exclude_unset=True).items() if v is not None}
    if "image" in update_data:
        update_data["image"] = str(update_data["image"])
    updated = await db["products"].find_one_and_update(
        {"_id": ObjectId(product_id)},
        {"$set": update_data},
        return_document=True
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    if updated.get("name") is None or updated.get("stock") is None:
        raise HTTPException(status_code=500, detail="Product missing required fields")
    updated["id"] = str(updated["_id"])
    updated.pop("_id", None)
    return updated

@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: str, user=Depends(get_current_user)):
    require_admin(user)
    result = await db["products"].delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return
