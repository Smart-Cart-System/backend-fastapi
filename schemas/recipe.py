from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class RecipeBase(BaseModel):
    session_id: int
    title: str
    title_ar: Optional[str] = None
    ingredients: str
    ingredients_ar: Optional[str] = None
    instructions: str
    instructions_ar: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None

class RecipeCreate(RecipeBase):
    pass

class Recipe(RecipeBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class RecipeResponse(BaseModel):
    id: int
    session_id: int
    title: str
    title_ar: Optional[str] = None
    ingredients: List[Any]
    ingredients_ar: Optional[List[Any]] = None
    instructions: Union[List[str], str]
    instructions_ar: Optional[Union[List[str], str]] = None
    description: Optional[str] = ""
    description_ar: Optional[str] = ""
    created_at: datetime

class RecipeList(BaseModel):
    recipes: List[RecipeResponse]