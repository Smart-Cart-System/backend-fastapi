import json
import os
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models.recipe import Recipe
from crud.cart_item import get_cart_items_by_session
import logging
from openai import AsyncOpenAI

# Set up logging
logger = logging.getLogger(__name__)

# Initialize AsyncOpenAI client with API key from environment
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

async def generate_recipe_from_items(db: Session, session_id: int) -> Dict[str, Any]:
    """
    Generate a recipe based on items purchased in a session using ChatGPT
    """
    # Get cart items from the session
    items, _ = get_cart_items_by_session(db, session_id)
    
    if not items or len(items) == 0:
        return {"error": "No items found in this session"}
    
    # Extract product names from cart items
    ingredients = []
    for item in items:
        if hasattr(item, 'product') and item.product:
            product_name = item.product.description
            quantity = item.quantity
            
            # If it has a weight, include that
            if item.saved_weight:
                ingredients.append(f"{product_name} ({item.saved_weight} kg)")
            else:
                ingredients.append(f"{product_name} (x{quantity})")
    
    if not ingredients:
        return {"error": "No valid ingredients found"}
    
    # Prepare prompt for ChatGPT to generate bilingual recipe
    prompt = f"""
    Generate a recipe using some or all of these ingredients:
    {', '.join(ingredients)}
    
    Format your response as a JSON object with these fields in BOTH English and Arabic:
    1. title: The name of the recipe in English
    2. title_ar: The name of the recipe in Arabic
    3. ingredients: A list of ingredients with amounts in English
    4. ingredients_ar: A list of ingredients with amounts in Arabic
    5. instructions: Step-by-step cooking instructions in English
    6. instructions_ar: Step-by-step cooking instructions in Arabic
    7. description: A short description of the dish in English
    8. description_ar: A short description of the dish in Arabic
    
    Only include ingredients that would make sense together in a recipe. You don't have to use all ingredients.
    
    Example format:
    {{
      "title": "English Recipe Title",
      "title_ar": "عنوان الوصفة بالعربية",
      "ingredients": ["Ingredient 1", "Ingredient 2"],
      "ingredients_ar": ["المكون 1", "المكون 2"],
      "instructions": ["Step 1", "Step 2"],
      "instructions_ar": ["الخطوة 1", "الخطوة 2"],
      "description": "English description",
      "description_ar": "الوصف بالعربية"
    }}
    """
    
    try:
        # Call ChatGPT API with AsyncOpenAI client
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful cooking assistant that creates recipes in both English and Arabic based on available ingredients."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500  # Increased token limit for bilingual content
        )
        
        # Extract recipe from response
        recipe_text = response.choices[0].message.content
        
        # Try to parse as JSON
        try:
            # Sometimes the API returns markdown-formatted JSON
            if "```json" in recipe_text:
                recipe_text = recipe_text.split("```json")[1].split("```")[0].strip()
            elif "```" in recipe_text:
                recipe_text = recipe_text.split("```")[1].strip()
            
            recipe_data = json.loads(recipe_text)
            
            # Create recipe object to save to database
            # Always store as JSON strings in the database
            recipe = Recipe(
                session_id=session_id,
                title=recipe_data["title"],
                title_ar=recipe_data.get("title_ar", ""),
                ingredients=json.dumps(recipe_data["ingredients"]),
                ingredients_ar=json.dumps(recipe_data.get("ingredients_ar", [])),
                instructions=json.dumps(recipe_data["instructions"]) 
                    if isinstance(recipe_data["instructions"], list) 
                    else json.dumps([recipe_data["instructions"]]),
                instructions_ar=json.dumps(recipe_data.get("instructions_ar", [])) 
                    if isinstance(recipe_data.get("instructions_ar", []), list) 
                    else json.dumps([recipe_data.get("instructions_ar", "")]),
                description=recipe_data.get("description", ""),
                description_ar=recipe_data.get("description_ar", "")
            )
            
            # Save to database
            db.add(recipe)
            db.commit()
            db.refresh(recipe)
            
            # Return complete recipe data with original formats for the API response
            return {
                "id": recipe.id,
                "session_id": recipe.session_id,
                "title": recipe.title,
                "title_ar": recipe.title_ar,
                "ingredients": recipe_data["ingredients"],
                "ingredients_ar": recipe_data.get("ingredients_ar", []),
                "instructions": recipe_data["instructions"],
                "instructions_ar": recipe_data.get("instructions_ar", []),
                "description": recipe_data.get("description", ""),
                "description_ar": recipe_data.get("description_ar", ""),
                "created_at": recipe.created_at
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse recipe as JSON: {e}")
            return {
                "error": "Failed to parse generated recipe",
                "raw_response": recipe_text
            }
            
    except Exception as e:
        logger.error(f"ChatGPT API error: {e}")
        return {"error": f"Failed to generate recipe: {str(e)}"}