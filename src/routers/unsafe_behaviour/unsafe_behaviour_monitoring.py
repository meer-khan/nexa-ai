from datetime import datetime
from pymongo import ASCENDING
from datetime import datetime, timezone, timedelta
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)
from pymongo.collection import Collection
from typing_extensions import Dict, List
from db.db_models import create_models
from schemas.unsafe_behaviour_schemas import ViolationRequest
import pytz
import asyncio
from icecream import ic

router = APIRouter(tags=["unsafe-behaviour"], prefix="/violations")
collections: Dict[str, Collection] = create_models()
# Store active WebSocket connections
active_connections: List[WebSocket] = []

@router.post(path="/unsafe-behaviour")
async def record_violation(violation: ViolationRequest):
    # Validate against allowed violation types
    violation_data = violation.model_dump()
    date_time = datetime.now(timezone.utc)
    violation_data["createdAt"] = date_time
    # Save violation to the database
    result = collections.get("violations").insert_one(violation_data)

    # Broadcast the violation to all connected WebSocket clients
    await broadcast({
        "id": str(result.inserted_id),
        "camera_id": violation.camera_id,
        "timestamp": date_time,
        "violations": violation.violations
    })

    return {"message": "Violation recorded successfully", "id": str(result.inserted_id)}

# @router.websocket("/realtime")
# async def websocket_endpoint(websocket: WebSocket):
#     # Accept and store the WebSocket connection
#     await websocket.accept()
#     active_connections.append(websocket)

#     try:
#         while True:
#             await websocket.receive_text()  # Keep the connection alive
#     except WebSocketDisconnect:
#         active_connections.remove(websocket)
#         print("Client disconnected")

# # Helper function to broadcast data to connected clients
# async def broadcast(data: dict):
#     for connection in active_connections:
#         await connection.send_json(data)







# Add a connection to the active list
async def connect(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

# Remove a connection from the active list
async def disconnect(websocket: WebSocket):
    active_connections.remove(websocket)

# Broadcast a message to all active connections
async def broadcast(message: dict):
    for connection in active_connections:
        await connection.send_json(message)

# Fetch the last recorded record from the database
def get_last_record():
    last_record = None
    last_record = collections.get("violations").find_one(sort=[("_id", -1)])
    if last_record:
        last_record.pop("_id")  # Convert ObjectId to string
    
    ic
    return last_record

# WebSocket endpoint
@router.websocket("/violation-updates")
async def websocket_endpoint(websocket: WebSocket):
    await connect(websocket)
    try:
        # Send the last recorded record when a new connection is established
        last_record = get_last_record()
        if last_record:
            await websocket.send_json({"type": "last_record", "data": last_record})

        while True:
            # Keep the WebSocket connection alive
            await asyncio.sleep(0.5)  # Adjust polling interval as necessary

            # Fetch recent events
            recent_events = get_recent_events()
            if recent_events:
                await broadcast({"type": "recent_events", "data": recent_events})

    except WebSocketDisconnect:
        await disconnect(websocket)