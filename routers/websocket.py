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
 
@router.websocket("/cart")
async def websocket_cart_endpoint(websocket: WebSocket):
    await websocket.accept()
    cart_id = None
    
    # Receive the initial message containing the cart_id
    try:
        data = await websocket.receive_json()
        cart_id = data.get("cart_id")
        
        if not cart_id:
            await websocket.send_json({"error": "No cart_id provided"})
            await websocket.close()
            return
            
        # Get cart and validate
        cart = get_cart_by_id(cart_id)
        if not cart:
            await websocket.send_json({"error": "Invalid cart_id"})
            await websocket.close()
            return
            
        # Store connection in service layer
        await register_hardware_client(cart_id, websocket)
        await websocket.send_json({"status": "connected", "message": "Cart connection established"})
        
        # Keep connection open and handle status updates
        while True:
            data = await websocket.receive_json()
            cart_id = data.get("cart_id")
            status = data.get("status")
            ip = data.get("ip")
            
            if status == "online" and cart_id:
                # Refresh the connection in our service
                await register_hardware_client(cart_id, websocket)
                logging.info(f"Cart {cart_id} status: online, IP: {ip}")
        
    except WebSocketDisconnect:
        if cart_id:
            logging.info(f"Cart {cart_id} disconnected")
            await remove_hardware_client(cart_id)
    except Exception as e:
        logging.error(f"Error in cart websocket: {e}")
        await websocket.close()