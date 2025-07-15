from pydantic import BaseModel
from typing import Optional

class ReviewBase(BaseModel):
    rating: int  # 1-5
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewOut(ReviewBase):
    id: str
    user_id: str
    product_id: str
