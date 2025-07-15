from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class CartItem(BaseModel):
    product_id: str
    quantity: int

class CartOut(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    items: List[CartItem]
    updated_at: datetime

    class Config:
        allow_population_by_field_name = True
