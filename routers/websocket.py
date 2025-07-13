from modulefinder import test
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import logging
from crud import cart_item
from crud.cart import get_cart_by_id
from sqlalchemy.orm import Session
from database import get_db
from core.security import get_current_user
from models.user import User
from crud.customer_session import get_active_session_by_user
from core.security import verify_pi_api_key
from services.websocket_service import (
    register_client, 
    register_hardware_client, 
    remove_client, 
    remove_hardware_client,
    echo as echo_service,
    echo_hardware_clients as echo_hardware_service
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

@router.post("/echo")
async def echo_hardware_message(message: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Here you can add logic to process the echo message
    logging.info(f"Echoing message from user {current_user.id}: {message}")
    user = get_active_session_by_user(db,current_user.id)
    if await echo_service(user.session_id, message):
        return {"status": "success"}
    return {"status": "error"}

@router.post("/echo/hardware/{cart_id}")
async def echo_hardware_message(cart_id: int, session_id: int, message: str, db: Session = Depends(get_db)):
    logging.info(f"Echoing hardware message from user {cart_id}: {message}")
    if await echo_hardware_service(cart_id,session_id, message):
        return {"status": "success"}
    return {"status": "error"}