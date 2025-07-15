from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class OrderItem(BaseModel):
    product_id: str
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItem]
    total: float

class OrderOut(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    items: List[OrderItem]
    total: float
    status: str
    created_at: datetime

    class Config:
        allow_population_by_field_name = True
