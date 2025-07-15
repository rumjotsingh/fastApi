from pydantic import BaseModel, Field
from typing import Optional

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class CategoryOut(CategoryBase):
    id: str = Field(..., alias="_id")

    class Config:
        allow_population_by_field_name = True
