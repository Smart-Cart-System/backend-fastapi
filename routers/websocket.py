from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict
import logging
from crud import cart_item
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(
    prefix="/ws",
    tags=["websocket"]
)

cart_clients: Dict[int, WebSocket] = {}

@router.websocket("/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int, db: Session = Depends(get_db)):
    await websocket.accept()

    session = cart_item.validate_session(db, session_id)
    if not session:
        await websocket.send_json({"Message": "Web socket connection cannot be established"})
        await websocket.close()
    else:
        await websocket.send_json({"Message": "Web socket connection established"})
        cart_clients[session_id] = websocket
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            cart_clients.pop(session_id, None)
 

   
async def notify_clients(session_id: int, message_type: str, barcode: int):
    if session_id in cart_clients:
        client = cart_clients[session_id]
        try:
            logging.info(f"Sending message to session {session_id}: {message_type}")
            await client.send_json({"type": message_type, "data" : barcode})
        except Exception as e:
            logging.error(f"Failed to send message: {e}")