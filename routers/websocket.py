from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import logging
from crud import cart_item
from crud.cart import get_cart_by_id
from sqlalchemy.orm import Session
from database import get_db
from services.websocket_service import (
    register_client, 
    register_hardware_client, 
    remove_client, 
    remove_hardware_client
)

router = APIRouter(
    prefix="/ws",
    tags=["websocket"]
)

@router.websocket("/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int, db: Session = Depends(get_db)):
    await websocket.accept()

    session = cart_item.validate_session(db, session_id)
    if not session:
        await websocket.send_json({"Message": "Web socket connection cannot be established"})
        await websocket.close()
    else:
        await websocket.send_json({"Message": "Web socket connection established"})
        await register_client(session_id, websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            await remove_client(session_id)
 
@router.websocket("/hardware/{cart_id}")
async def websocket_cart_endpoint(websocket: WebSocket, cart_id: int, db: Session = Depends(get_db)):
    await websocket.accept()
    
    try:
        # Validate cart exists before processing
        cart = get_cart_by_id(db, cart_id)
        if not cart:
            await websocket.send_json({"error": "Cart not found"})
            await websocket.close()
            return
            
        # Register hardware connection
        await register_hardware_client(cart_id, websocket)
        await websocket.send_json({"status": "connected", "message": "Hardware connection established"})
        
        # Keep connection alive
        while True:
            # Process incoming messages
            data = await websocket.receive_json()
            # Add any message handling logic here if needed
            
    except WebSocketDisconnect:
        logging.info(f"Cart {cart_id} disconnected")
        await remove_hardware_client(cart_id)
    except Exception as e:
        logging.error(f"WebSocket error: {str(e)}")
        await websocket.close()