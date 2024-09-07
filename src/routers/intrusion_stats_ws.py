from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)
from pymongo.collection import Collection
from src.analysis.log_entry_exit_helper import (
    count_entries_last_24_hours,
    count_known_unknown_people,
    count_exits_last_24_hours,
    count_people_by_location,
    count_people_in_factory,
)
from typing_extensions import Dict, List
from db.db_models import create_models

router = APIRouter(tags=["intrustion-stats"], prefix="/intrusion-stats")
collections: Dict[str,Collection] = create_models()


# List to keep track of active WebSocket connections
active_connections: List[WebSocket] = []


async def connect(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)


async def disconnect(websocket: WebSocket):
    active_connections.remove(websocket)


async def broadcast(message: dict):
    for connection in active_connections:
        await connection.send_json(message)


@router.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    await connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect:
        await disconnect(websocket)


# Function to broadcast analysis results to connected clients
async def broadcast_analysis():
    message = {
        "entries_last_24_hours": count_entries_last_24_hours(),
        "exits_last_24_hours": count_exits_last_24_hours(),
        "people_in_factory": count_people_in_factory(),
        "known_people_in_factory": count_known_unknown_people()[0],
        "unknown_people_in_factory": count_known_unknown_people()[1],
        "people_by_location": {},  # This will be populated for specific locations
    }

    # Get the number of people at each location
    locations = collections.get("cameras").distinct("location")
    for location in locations:
        message["people_by_location"][location] = count_people_by_location(location)

    await broadcast(message)

