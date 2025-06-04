from sqlalchemy.orm import Session
import json
from models.recipe import Recipe
from schemas.recipe import RecipeCreate, RecipeResponse
from typing import List, Optional

def create_recipe(db: Session, recipe: RecipeCreate) -> Recipe:
    """Create a new recipe"""
    db_recipe = Recipe(**recipe.dict())
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe

def get_recipes_by_session(db: Session, session_id: int) -> List[Recipe]:
    """Get all recipes for a session"""
    return db.query(Recipe).filter(Recipe.session_id == session_id).all()

def get_recipe_by_id(db: Session, recipe_id: int) -> Optional[Recipe]:
    """Get a specific recipe by ID"""
    return db.query(Recipe).filter(Recipe.id == recipe_id).first()

def recipe_to_response(recipe: Recipe) -> RecipeResponse:
    """Convert a recipe model to a response schema with bilingual content"""
    try:
        # Parse ingredients JSON strings from database
        ingredients = json.loads(recipe.ingredients)
        ingredients_ar = json.loads(recipe.ingredients_ar) if recipe.ingredients_ar else []
        
        # Parse instructions JSON strings
        if recipe.instructions.startswith("[") or recipe.instructions.startswith("{"):
            instructions = json.loads(recipe.instructions)
        else:
            instructions = recipe.instructions
            
        if recipe.instructions_ar and (recipe.instructions_ar.startswith("[") or recipe.instructions_ar.startswith("{")):
            instructions_ar = json.loads(recipe.instructions_ar)
        else:
            instructions_ar = recipe.instructions_ar
            
        return RecipeResponse(
            id=recipe.id,
            session_id=recipe.session_id,
            title=recipe.title,
            title_ar=recipe.title_ar,
            ingredients=ingredients,
            ingredients_ar=ingredients_ar,
            instructions=instructions,
            instructions_ar=instructions_ar,
            description=recipe.description or "",
            description_ar=recipe.description_ar or "",
            created_at=recipe.created_at
        )
    except json.JSONDecodeError:
        # Fallback in case of parsing issues
        return RecipeResponse(
            id=recipe.id,
            session_id=recipe.session_id,
            title=recipe.title,
            title_ar=recipe.title_ar or "",
            ingredients=[],
            ingredients_ar=[],
            instructions="Unable to parse recipe data",
            instructions_ar="",
            description=recipe.description or "",
            description_ar=recipe.description_ar or "",
            created_at=recipe.created_at
        )