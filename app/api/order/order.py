from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime
from app.db.connection import db
from app.core.security import get_current_user
from app.schemas.order import OrderCreate, OrderOut

router = APIRouter()

# Create new order
@router.post("/", response_model=OrderOut)
async def create_order(order: OrderCreate, current_user: dict = Depends(get_current_user)):
    total = 0.0
    items_data = []

    # Validate product IDs & calculate total price
    for item in order.items:
        product = await db["products"].find_one({"_id": ObjectId(item.product_id), "is_active": True})
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} not found or inactive")
        item_total = product["price"] * item.quantity
        total += item_total
        items_data.append({"product_id": item.product_id, "quantity": item.quantity})

    order_data = {
        "user_id": str(current_user["_id"]),
        "items": items_data,
        "total": round(total, 2),
        "status": "pending",
        "created_at": datetime.utcnow()
    }

    result = await db["orders"].insert_one(order_data)
    order_data["_id"] = str(result.inserted_id)
    return order_data

# Get my orders
@router.get("/my", response_model=list[OrderOut])
async def list_my_orders(current_user: dict = Depends(get_current_user)):
    orders = await db["orders"].find({"user_id": str(current_user["_id"])}).to_list(100)
    for o in orders:
        o["_id"] = str(o["_id"])
    return orders

# Get single order
@router.get("/{order_id}", response_model=OrderOut)
async def get_my_order(order_id: str, current_user: dict = Depends(get_current_user)):
    order = await db["orders"].find_one({"_id": ObjectId(order_id)})
    if not order or order["user_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=404, detail="Order not found")
    order["_id"] = str(order["_id"])
    return order

# Admin: list all orders
@router.get("/", response_model=list[OrderOut])
async def list_all_orders(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    orders = await db["orders"].find().to_list(100)
    for o in orders:
        o["_id"] = str(o["_id"])
    return orders

# Admin: update order status
@router.put("/{order_id}", response_model=OrderOut)
async def update_order(order_id: str, status: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    result = await db["orders"].update_one({"_id": ObjectId(order_id)}, {"$set": {"status": status}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    order = await db["orders"].find_one({"_id": ObjectId(order_id)})
    order["_id"] = str(order["_id"])
    return order
