from pydantic import BaseModel, HttpUrl
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category: Optional[str] = None         # e.g., "Electronics"
    brand: Optional[str] = None            # e.g., "Apple"
    image: Optional[HttpUrl] = None        # main product image URL
    rating: Optional[float] = 0.0          # average user rating
    num_reviews: Optional[int] = 0         # total number of reviews
    is_active: Optional[bool] = True       # active/inactive product

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    image: Optional[HttpUrl] = None
    rating: Optional[float] = None
    num_reviews: Optional[int] = None
    is_active: Optional[bool] = None

class ProductOut(ProductBase):
    id: str
