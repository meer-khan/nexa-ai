from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pymongo.collection import Collection
from db.db_models import create_models
from typing_extensions import Dict, List
from icecream import ic
import datetime

router = APIRouter(tags=["timerange-stats"], prefix="/ws/stats")
collections: Dict[str, Collection] = create_models()


# Helper function to get current UTC time and 60 minutes back in UTC
def get_last_60_minutes_range():
    current_time_utc = datetime.datetime.now(datetime.timezone.utc)
    past_time_utc = current_time_utc - datetime.timedelta(minutes=60)
    return past_time_utc, current_time_utc


def get_last_24_hours_range():
    current_time_utc = datetime.datetime.now(datetime.timezone.utc)
    past_time_utc = current_time_utc - datetime.timedelta(hours=24)
    return past_time_utc, current_time_utc


def check_assembly_line_activity_last_60min():
    start_time_60min_utc, end_time_60min_utc = get_last_60_minutes_range()

    # Get time range for the last 24 hours
    start_time_24hr_utc, end_time_24hr_utc = get_last_24_hours_range()

    # Get camera IDs for 'assembly_line' areas
    assembly_line_camera_ids = [
        cam["cameraId"]
        for cam in collections.get("cameras").find({"cameraType": "assembly_line"}, {"_id": 0})
    ]

    # Get entry and exit camera IDs
    entry_camera_ids = [
        cam["cameraId"]
        for cam in collections.get("cameras").find({"cameraType": "entry"}, {"_id": 0})
    ]
    exit_camera_ids = [
        cam["cameraId"]
        for cam in collections.get("cameras").find({"cameraType": "exit"},  {"_id": 0})
    ]

    # Query for workers detected in the 'assembly_line' area in the last 60 minutes
    workers_detected_last_60_minutes = list(
        collections.get("entry_exit_logs").find(
            {
                "cameraId": {"$in": assembly_line_camera_ids},
                "createdAt": {"$gte": start_time_60min_utc, "$lte": end_time_60min_utc},
            },
             {"_id": 0}
        )
    )

    # Query for entry logs in the last 24 hours
    entries_last_24_hours = list(
        collections.get("entry_exit_logs").find(
            {
                "cameraId": {"$in": entry_camera_ids},
                "createdAt": {"$gte": start_time_24hr_utc, "$lte": end_time_24hr_utc},
            },
             {"_id": 0}
        )
    )

    # Query for exit logs in the last 24 hours
    exits_last_24_hours = list(
        collections.get("entry_exit_logs").find(
            {
                "cameraId": {"$in": exit_camera_ids},
                "createdAt": {"$gte": start_time_24hr_utc, "$lte": end_time_24hr_utc},
            },
             {"_id": 0}
        )
    )

    # Query for assembly line logs in the last 24 hours
    assembly_line_logs_last_24_hours = list(
        collections.get("entry_exit_logs").find(
            {
                "cameraId": {"$in": assembly_line_camera_ids},
                "createdAt": {"$gte": start_time_24hr_utc, "$lte": end_time_24hr_utc},
            },
            {"_id": 0}
        )
    )

    # Prepare the data to send back via WebSocket
    data_to_send = {
        "workers_detected_last_60_minutes": [
            {
                "employeeID": worker.get("employeeID"),
                "name": worker.get("name"),
                "timestamp": worker.get("createdAt").strftime('%Y-%m-%d %H:%M:%S'),
            }
            for worker in workers_detected_last_60_minutes
        ],
        "entries_last_24_hours": [
            {
                "employeeID": log.get("employeeID"),
                "name": log.get("name"),
                "timestamp": log.get("createdAt").strftime('%Y-%m-%d %H:%M:%S'),
            }
            for log in entries_last_24_hours
        ],
        "exits_last_24_hours": [
            {
                "employeeID": log.get("employeeID"),
                "name": log.get("name"),
                "timestamp": log.get("createdAt").strftime('%Y-%m-%d %H:%M:%S'),
            }
            for log in exits_last_24_hours
        ],
        "assembly_line_logs_last_24_hours": [
            {
                "employeeID": log.get("employeeID"),
                "name": log.get("name"),
                "timestamp": log.get("createdAt").strftime('%Y-%m-%d %H:%M:%S'),
            }
            for log in assembly_line_logs_last_24_hours
        ],
    }
    ic(data_to_send)
    return data_to_send


active_connections: List[WebSocket] = []


async def connect(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)


async def disconnect(websocket: WebSocket):
    active_connections.remove(websocket)


async def broadcast(message: dict):
    for connection in active_connections:
        await connection.send_json(message)


@router.websocket("/assembly-line-and-24hours-logs")
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
        "60_minutes_assembly_line_results": check_assembly_line_activity_last_60min(),
    }
    ic(message)
    await broadcast(message)
