from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from typing import List
import tempfile
import os
from google.cloud import vision
import time

from database import get_db
from core.security import get_current_user
from models.user import User
from schemas.checklist import ChecklistCreate, ChecklistItemCreate
from crud import checklist as checklist_crud

router = APIRouter(
    prefix="/ocr",
    tags=["ocr"]
)

def process_image_with_ocr(image_content: bytes) -> List[str]:
    """Process image content with Google Cloud Vision OCR and return extracted items"""
    # Create a temporary file to store the image
    with tempfile.NamedTemporaryFile(delete=False) as temp_image:
        temp_image.write(image_content)
        temp_image_path = temp_image.name
    
    try:
        # Get credentials path from environment variable or use hardcoded path as fallback
        credentials_path = os.environ.get(
            "GOOGLE_APPLICATION_CREDENTIALS", 
            "/home/smartcart/backend-fastapi/google_ocr.json"
        )
        
        # Debug logging to help diagnose the issue
        print(f"Looking for credentials file at: {credentials_path}")
        print(f"File exists: {os.path.exists(credentials_path)}")
        
        # Explicitly initialize the client with the credentials file
        client = vision.ImageAnnotatorClient.from_service_account_json(credentials_path)
        
        # Create an image object
        image = vision.Image(content=image_content)
        
        # Perform document text detection
        response = client.document_text_detection(image=image)
        
        # Extract lines instead of individual words
        extracted_items = []
        
        # Option 1: Extract full lines from text annotations
        if response.text_annotations:
            # The first text_annotation contains the entire text
            full_text = response.text_annotations[0].description
            # Split by newlines to get individual lines
            lines = full_text.split('\n')
            # Filter out empty lines and single characters
            extracted_items = [line.strip() for line in lines if line.strip() and len(line.strip()) > 1]
        
        # Option 2 (fallback): Try to reconstruct lines from blocks
        if not extracted_items and response.full_text_annotation:
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    # Group words by their vertical position to form lines
                    lines = {}
                    for paragraph in block.paragraphs:
                        if paragraph.confidence > 0.8:
                            # Get paragraph bounding box to determine the line
                            if paragraph.bounding_box:
                                # Use the top y-coordinate as a key to group words on same line
                                y_position = paragraph.bounding_box.vertices[0].y
                                
                                # Create the line text by joining all words
                                line_text = " ".join([
                                    "".join([symbol.text for symbol in word.symbols])
                                    for word in paragraph.words
                                ])
                                
                                # Add or append to line with this y-position
                                if y_position in lines:
                                    lines[y_position] += " " + line_text
                                else:
                                    lines[y_position] = line_text
                    
                    # Add all lines from this block
                    for line_text in lines.values():
                        if line_text and len(line_text) > 1:
                            extracted_items.append(line_text.strip())
        
        return extracted_items
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing error: {str(e)}"
        )
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_image_path):
            os.unlink(temp_image_path)

@router.post("/create-checklist", status_code=status.HTTP_201_CREATED)
async def create_checklist_from_image(
    image: UploadFile = File(...),
    checklist_name: str = Form("My OCR Checklist"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new checklist from text extracted from an uploaded image.
    The image is processed using OCR to extract items.
    """
    # Validate the file is an image
    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Read the image content
    image_content = await image.read()
    
    # Process image with OCR
    extracted_items = process_image_with_ocr(image_content)
    
    if not extracted_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No text could be extracted from the image"
        )
    
    # Create checklist items from extracted text
    checklist_items = [
        ChecklistItemCreate(text=item, checked=False)
        for item in extracted_items
    ]
    
    # Create the checklist
    checklist_data = ChecklistCreate(
        name=checklist_name,
        items=checklist_items
    )
    
    # Save to database
    new_checklist = checklist_crud.create_checklist(db, checklist_data, current_user.id)
    
    return {
        "message": "Checklist created successfully from image",
        "checklist_id": new_checklist.id,
        "name": new_checklist.name,
        "items_count": len(extracted_items),
        "items": [item.text for item in checklist_items]
    }