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
from utils.time_utilities import convert_utc_to_pst

router = APIRouter(tags=["unsafe-behaviour"], prefix="")
collections: Dict[str, Collection] = create_models()
# Store active WebSocket connections
active_connections: List[WebSocket] = []

@router.post(path="/violations")
async def record_violation(violation: ViolationRequest):
    # Validate against allowed violation types
    violation_data = violation.model_dump()
    date_time = datetime.now(timezone.utc)
    violation_data["createdAt"] = date_time
    result = collections.get("violations").insert_one(violation_data)

    # Broadcast the violation to all connected WebSocket clients
    await broadcast({
        "id": str(result.inserted_id),
        "camera_id": violation.camera_id,
        "timestamp": convert_utc_to_pst(date_time).strftime("%Y-%m-%d %H:%M:%S"),
        "violations": violation.violations
    })

    return {"message": "Violation recorded successfully", "id": str(result.inserted_id)}

async def connect(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

async def disconnect(websocket: WebSocket):
    active_connections.remove(websocket)

# Broadcast a message to all active connections
async def broadcast(message: dict):
    for connection in active_connections:
        await connection.send_json(message)

# Fetch the last recorded record from the database
async def get_last_record():
    last_record = None
    last_record = collections.get("violations").find_one(sort=[("_id", -1)], projection = {"_id": 0})
    if last_record:
        last_record["timestamp"] = convert_utc_to_pst(utc_time=last_record.get("createdAt")).strftime("%Y-%m-%d %H:%M:%S")
        last_record.pop("createdAt")
        last_record = {"violations": last_record}
    await broadcast(last_record)
    return last_record

# WebSocket endpoint
@router.websocket("/ws/violations/updates")
async def websocket_endpoint(websocket: WebSocket):
    await connect(websocket)
    
        # Send the last recorded record when a new connection is established
    await get_last_record()
    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect:
        await disconnect(websocket)