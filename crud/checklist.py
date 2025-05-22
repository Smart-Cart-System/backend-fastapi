from sqlalchemy.orm import Session
from models.checklist import Checklist, ChecklistItem
from schemas.checklist import ChecklistCreate, ChecklistUpdate, ChecklistItemCreate, ChecklistItemUpdate

def create_checklist(db: Session, checklist: ChecklistCreate, user_id: int):
    db_checklist = Checklist(name=checklist.name, user_id=user_id)
    db.add(db_checklist)
    db.commit()
    db.refresh(db_checklist)
    
    # Add items if provided
    for item in checklist.items:
        db_item = ChecklistItem(text=item.text, checked=item.checked, checklist_id=db_checklist.id)
        db.add(db_item)
    
    db.commit()
    db.refresh(db_checklist)
    return db_checklist

def get_checklist(db: Session, checklist_id: int, user_id: int):
    return db.query(Checklist).filter(
        Checklist.id == checklist_id, 
        Checklist.user_id == user_id
    ).first()

def get_user_checklists(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Checklist).filter(
        Checklist.user_id == user_id
    ).offset(skip).limit(limit).all()

def update_checklist_name(db: Session, checklist_id: int, user_id: int, name: str):
    checklist = get_checklist(db, checklist_id, user_id)
    if not checklist:
        return None
        
    checklist.name = name
    db.commit()
    db.refresh(checklist)
    return checklist

def delete_checklist(db: Session, checklist_id: int, user_id: int):
    checklist = get_checklist(db, checklist_id, user_id)
    if not checklist:
        return False
        
    db.delete(checklist)
    db.commit()
    return True

# Checklist Item Operations
def add_checklist_item(db: Session, checklist_id: int, user_id: int, item: ChecklistItemCreate):
    checklist = get_checklist(db, checklist_id, user_id)
    if not checklist:
        return None
        
    db_item = ChecklistItem(
        text=item.text, 
        checked=item.checked, 
        checklist_id=checklist_id
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_checklist_item(db: Session, item_id: int, checklist_id: int, user_id: int):
    checklist = get_checklist(db, checklist_id, user_id)
    if not checklist:
        return None
    
    return db.query(ChecklistItem).filter(
        ChecklistItem.id == item_id, 
        ChecklistItem.checklist_id == checklist_id
    ).first()

def update_checklist_item(db: Session, item_id: int, checklist_id: int, user_id: int, item_update: ChecklistItemUpdate):
    db_item = get_checklist_item(db, item_id, checklist_id, user_id)
    if not db_item:
        return None
    
    if item_update.text is not None:
        db_item.text = item_update.text
    if item_update.checked is not None:
        db_item.checked = item_update.checked
    
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_checklist_item(db: Session, item_id: int, checklist_id: int, user_id: int):
    db_item = get_checklist_item(db, item_id, checklist_id, user_id)
    if not db_item:
        return False
    
    db.delete(db_item)
    db.commit()
    return True