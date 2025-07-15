from fastapi import APIRouter, Depends, HTTPException
from app.db.connection import db
from app.core.security import get_current_user
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/admin/stats")
async def get_admin_stats(current_user: dict = Depends(get_current_user)):
    # Only admin can access
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    # Total counts
    total_users = await db["users"].count_documents({})
    total_products = await db["products"].count_documents({})
    total_orders = await db["orders"].count_documents({})

    # Total revenue
    pipeline = [
        {"$group": {"_id": None, "total": {"$sum": "$total"}}}
    ]
    revenue_result = await db["orders"].aggregate(pipeline).to_list(1)
    total_revenue = revenue_result[0]["total"] if revenue_result else 0

    # Daily revenue (today)
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    daily_pipeline = [
        {"$match": {"created_at": {"$gte": today, "$lt": tomorrow}}},
        {"$group": {"_id": None, "total": {"$sum": "$total"}}}
    ]
    daily_result = await db["orders"].aggregate(daily_pipeline).to_list(1)
    daily_revenue = daily_result[0]["total"] if daily_result else 0

    # Monthly revenue (current month)
    first_of_month = today.replace(day=1)
    next_month = (first_of_month + timedelta(days=32)).replace(day=1)

    monthly_pipeline = [
        {"$match": {"created_at": {"$gte": first_of_month, "$lt": next_month}}},
        {"$group": {"_id": None, "total": {"$sum": "$total"}}}
    ]
    monthly_result = await db["orders"].aggregate(monthly_pipeline).to_list(1)
    monthly_revenue = monthly_result[0]["total"] if monthly_result else 0

    # Most sold products (top 5)
    top_products_pipeline = [
        {"$unwind": "$items"},  # Assuming order has "items": [{ product_id, quantity }]
        {"$group": {"_id": "$items.product_id", "total_sold": {"$sum": "$items.quantity"}}},
        {"$sort": {"total_sold": -1}},
        {"$limit": 5}
    ]
    top_products_result = await db["orders"].aggregate(top_products_pipeline).to_list(None)
    # Format: [{"product_id": "xxx", "total_sold": 10}, ...]
    top_products = [{"product_id": str(p["_id"]), "total_sold": p["total_sold"]} for p in top_products_result]

    # Pending vs delivered orders
    pending_count = await db["orders"].count_documents({"status": "pending"})
    delivered_count = await db["orders"].count_documents({"status": "delivered"})

    return {
        "total_users": total_users,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "daily_revenue": daily_revenue,
        "monthly_revenue": monthly_revenue,
        "pending_orders": pending_count,
        "delivered_orders": delivered_count,
        "top_products": top_products
    }
