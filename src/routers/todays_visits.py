from datetime import datetime, timedelta, timezone
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)

from pymongo.collection import Collection
from typing_extensions import Dict, List
from db.db_models import create_models
import pytz
from icecream import ic

router = APIRouter(tags=["todays-visits"], prefix="/ws/todays-visits")
collections: Dict[str, Collection] = create_models()


# Function to get the last 24 hours in UTC
def get_last_24_hours_utc_range():
    current_time_utc = datetime.now(timezone.utc)
    past_time_utc = current_time_utc - timedelta(hours=24)
    return past_time_utc, current_time_utc


# Function to convert UTC to Pakistan Standard Time (PST)
def convert_utc_to_pst(utc_time: datetime):
    pst_timezone = pytz.timezone("Asia/Karachi")  # Pakistan Standard Time
    return utc_time.astimezone(pst_timezone)


# Main function to fetch events from the last 24 hours
def fetch_last_24_hours_logs():
    start_time_utc, end_time_utc = get_last_24_hours_utc_range()

    # Get camera IDs for entry, exit, and assembly line types
    entry_camera_ids = [
        cam["cameraId"]
        for cam in collections.get("cameras").find({"cameraType": "entry"})
    ]
    exit_camera_ids = [
        cam["cameraId"]
        for cam in collections.get("cameras").find({"cameraType": "exit"})
    ]
    assembly_line_camera_ids = [
        cam["cameraId"]
        for cam in collections.get("cameras").find({"cameraType": "assembly_line"})
    ]

    # Query for entry logs in the last 24 hours
    entry_logs = list(
        collections.get("entry_exit_logs").find(
            {
                "cameraId": {"$in": entry_camera_ids},
                "createdAt": {"$gte": start_time_utc, "$lte": end_time_utc},
            },
            {"_id": 0},
        )
    )

    # Query for exit logs in the last 24 hours
    exit_logs = list(
        collections.get("entry_exit_logs").find(
            {
                "cameraId": {"$in": exit_camera_ids},
                "createdAt": {"$gte": start_time_utc, "$lte": end_time_utc},
            },
            {"_id": 0},
        )
    )

    # Query for assembly line logs in the last 24 hours
    assembly_line_logs = list(
        collections.get("entry_exit_logs").find(
            {
                "cameraId": {"$in": assembly_line_camera_ids},
                "createdAt": {"$gte": start_time_utc, "$lte": end_time_utc},
            },
            {"_id": 0},
        )
    )

    # Fetch camera details like location for each camera ID
    def get_camera_location(camera_id):
        camera = collections.get("cameras").find_one(
            {"cameraId": camera_id}, {"_id": 0}
        )
        return camera.get("location", "unknown")

    # Process the logs to return required details
    def process_logs(logs):
        processed_logs = []
        for log in logs:
            pst_time = convert_utc_to_pst(log["createdAt"])
            camera_location = get_camera_location(log["cameraId"])
            processed_logs.append(
                {
                    "name": log.get("name", "Unknown"),  # Fetch name if available
                    "employeeID": log.get("employeeID", "Unknown"),
                    "time_in_pst": pst_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "cameraID": log.get("cameraId", "Unknown"),
                    "camera_location": camera_location,
                }
            )
        return processed_logs

    # Process each type of log
    processed_entry_logs = process_logs(entry_logs)
    processed_exit_logs = process_logs(exit_logs)
    processed_assembly_line_logs = process_logs(assembly_line_logs)
    # Return the processed data
    return {
        "entry_logs": processed_entry_logs,
        "exit_logs": processed_exit_logs,
        "assembly_line_logs": processed_assembly_line_logs,
    }


active_connections: List[WebSocket] = []


async def connect(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)


async def disconnect(websocket: WebSocket):
    active_connections.remove(websocket)


async def broadcast(message: dict):
    for connection in active_connections:
        await connection.send_json(message)


@router.websocket("/all")
async def websocket_endpoint(websocket: WebSocket):
    await connect(websocket)
    await broadcast_analysis()
    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect:
        await disconnect(websocket)


# Function to broadcast analysis results to connected clients
async def broadcast_analysis():
    message = {
        "todays_visits": fetch_last_24_hours_logs(),
    }
    message.get("todays_visits").update(
        {
            "total_assembly_line_logs": len(
                message.get("todays_visits").get("assembly_line_logs")
            ), 
            "total_entry_logs": len(
                message.get("todays_visits").get("entry_logs")
            ), 
            "total_exit_logs":  len(
                message.get("todays_visits").get("exit_logs")
            )
        }
    )

    await broadcast(message)
