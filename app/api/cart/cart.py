from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime
from app.db.connection import db
from app.core.security import get_current_user
from app.schemas.cart import CartOut, CartItem
from app.utils.transform import mongo_obj_to_dict

router = APIRouter()

# POST /cart/add
@router.post("/add", response_model=CartOut)
async def add_to_cart(item: CartItem, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    cart = await db["cart"].find_one({"user_id": user_id})

    if cart:
        # check if product already in cart
        found = False
        for existing_item in cart["items"]:
            if existing_item["product_id"] == item.product_id:
                existing_item["quantity"] += item.quantity
                found = True
                break
        if not found:
            cart["items"].append(item.dict())
        await db["cart"].update_one({"_id": cart["_id"]}, {
            "$set": {"items": cart["items"], "updated_at": datetime.utcnow()}
        })
    else:
        # new cart
        cart = {
            "user_id": user_id,
            "items": [item.dict()],
            "updated_at": datetime.utcnow()
        }
        result = await db["cart"].insert_one(cart)
        cart["_id"] = result.inserted_id

    cart["_id"] = str(cart["_id"])
    return mongo_obj_to_dict(cart)

# GET /cart
@router.get("/", response_model=CartOut)
async def get_cart(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    cart = await db["cart"].find_one({"user_id": user_id})
    if not cart:
        # return empty cart if not exists
        cart = {
            "_id": "",
            "user_id": user_id,
            "items": [],
            "updated_at": datetime.utcnow()
        }
    else:
        cart["_id"] = str(cart["_id"])
    return mongo_obj_to_dict(cart)

# DELETE /cart/{product_id}
@router.delete("/{product_id}", response_model=CartOut)
async def remove_from_cart(product_id: str, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    cart = await db["cart"].find_one({"user_id": user_id})
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    new_items = [item for item in cart["items"] if item["product_id"] != product_id]
    await db["cart"].update_one({"_id": cart["_id"]}, {
        "$set": {"items": new_items, "updated_at": datetime.utcnow()}
    })
    cart["items"] = new_items
    cart["_id"] = str(cart["_id"])
    return mongo_obj_to_dict(cart)
