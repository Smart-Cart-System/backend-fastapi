import asyncio
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Union
from schemas.sse import SSEMessage
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from database import get_db
from pydantic import BaseModel
from schemas.sse import SSEAuthMessage


router = APIRouter(
    prefix="/sse",
    tags=["ss-events"]
)
clients = {}  # cart_id -> asyncio.Queue

async def event_stream(cart_id: str):
    queue = asyncio.Queue()
    clients[cart_id] = queue
    print(f"Added client {cart_id} to clients dictionary. Total clients: {len(clients)}")
    try:
        # Send initial message to establish connection
        initial_message = {"type": "connection", "message": f"Connected {cart_id}"}
        yield f"data: {json.dumps(initial_message)}\n\n"        
        while True:
            msg = await queue.get()
            print(f"Sending message to client {cart_id}: {msg}")
            yield f"data: {json.dumps(msg)}\n\n"
    except asyncio.CancelledError:
        print(f"{cart_id} disconnected")
    finally:
        clients.pop(cart_id, None)
        print(f"{cart_id} removed from clients. Remaining clients: {len(clients)}")

@router.get("/{cart_id}", 
    summary="Subscribe to SSE events for a cart",
    description="""
    Establishes a Server-Sent Events (SSE) connection for the specified cart ID.
    The client will receive real-time updates about cart events through this connection.
    The connection remains open until the client disconnects or the server closes it.
    """)
async def sse(cart_id: str, request: Request):
    print(f"New connection attempt from cart: {cart_id}")
    return StreamingResponse(
        event_stream(cart_id), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

async def send_authenticated_message(cart_id: str, auth_message: SSEAuthMessage):
    """
    Send an authenticated message to a specific client
    
    Args:
        cart_id: The ID of the client to send the message to
        auth_message: The authenticated message to send
    
    Returns:
        bool: True if message was sent successfully, False if client not found
    """

    cart_id = str(cart_id)

    print(f"Attempting to send message to client {cart_id}")
    print(f"Current clients: {list(clients.keys())}")
    
    queue = clients.get(cart_id)
    if queue:
        # Convert Pydantic model to dict for JSON serialization
        message_dict = auth_message.model_dump()
        print(f"Putting message in queue for client {cart_id}: {message_dict}")
        await queue.put(message_dict)
        return True
    else:
        print(f"Client {cart_id} not found in clients dictionary")
        return False


