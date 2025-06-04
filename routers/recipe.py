from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from typing import List
from schemas.recipe import RecipeResponse, RecipeList
from crud.recipe import get_recipes_by_session, get_recipe_by_id, recipe_to_response
from services.recipe_service import generate_recipe_from_items
from models.user import User
from core.security import get_current_user
from crud.customer_session import get_session

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"]
)

@router.get("/session/{session_id}", response_model=RecipeList)
async def get_recipes_for_session(
    session_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all recipes that have been generated for a particular session"""
    # Get the session to verify it belongs to the user
    session = get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check user authorization - only allow if it's the user's session or an admin
    if session.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this session's recipes")
    
    # Get recipes
    recipes = get_recipes_by_session(db, session_id)
    recipe_responses = [recipe_to_response(recipe) for recipe in recipes]
    
    return RecipeList(recipes=recipe_responses)

@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe_detail(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific recipe"""
    recipe = get_recipe_by_id(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Get the session to verify it belongs to the user
    session = get_session(db, recipe.session_id)
    
    # Check user authorization
    if session.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this recipe")
    
    return recipe_to_response(recipe)

@router.post("/generate/{session_id}", response_model=RecipeResponse)
async def generate_recipe(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a new recipe based on the items in a session"""
    # Get the session to verify it belongs to the user
    session = get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check user authorization
    if session.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to generate recipes for this session")
    
    # Generate recipe
    recipe_data = await generate_recipe_from_items(db, session_id)
    
    if "error" in recipe_data:
        raise HTTPException(status_code=400, detail=recipe_data["error"])
    
    return recipe_data