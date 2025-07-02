import logging
from typing import Dict, Any
from fastapi import WebSocket

# Connection managers
cart_clients: Dict[int, WebSocket] = {}
cart_clients_hardware: Dict[int, WebSocket] = {}

async def register_client(session_id: int, websocket: WebSocket) -> None:
    """Register a client websocket connection"""
    cart_clients[session_id] = websocket
    
async def register_hardware_client(cart_id: int, websocket: WebSocket) -> None:
    """Register a hardware client websocket connection"""
    cart_clients_hardware[cart_id] = websocket

async def remove_client(session_id: int) -> None:
    """Remove a client connection"""
    cart_clients.pop(session_id, None)
    
async def remove_hardware_client(cart_id: int) -> None:
    """Remove a hardware client connection"""
    cart_clients_hardware.pop(cart_id, None)

async def notify_clients(session_id: int, message_type: str, barcode: int) -> bool:
    """Send message to session clients"""
    if session_id in cart_clients:
        client = cart_clients[session_id]
        try:
            logging.info(f"Sending message to session {session_id}: {message_type}")
            await client.send_json({"type": message_type, "data": barcode})
            return True
        except Exception as e:
            logging.error(f"Failed to send message: {e}")
    return False

async def echo(session_id: int, message: str) -> bool:
    """Send echo to session clients"""
    if session_id in cart_clients:
        client = cart_clients[session_id]
        try:
            logging.info(f"Sending message to session {session_id}: {message}")
            await client.send_json({"message": message})
            return True
        except Exception as e:
            logging.error(f"Failed to send message: {e}")
    return False

async def notify_hardware_clients(cart_id: int, command: str, session_id: int) -> bool:
    """Send message to hardware clients"""
    if cart_id in cart_clients_hardware:
        client = cart_clients_hardware[cart_id]
        try:
            logging.info(f"Sending message to hardware client {cart_id}: {command}")
            await client.send_json({"type": command, "data": session_id})
            return True
        except Exception as e:
            logging.error(f"Failed to send message to hardware client: {e}")
    return False