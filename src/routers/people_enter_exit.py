from fastapi import APIRouter, HTTPException, status, Response,  WebSocket, WebSocketDisconnect
from src.routers.intrusion_stats_ws import broadcast_analysis
from pymongo.collection import Collection
from typing_extensions import Dict, Any
from src.schemas import data_schemas
from db.db_models import create_models
from icecream import ic
import datetime

router = APIRouter(tags=["entry-exit-logs"], prefix="/cameras")
collections: Dict[str, Collection] = create_models()


# Route to add a new camera
@router.post("/add_camera", status_code=status.HTTP_200_OK)
async def add_camera(camera_data: data_schemas.AddCamera, response: Response):

    if collections.get("cameras").find_one({"cameraId": camera_data.cameraId}):
        response.status_code = status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Camera id already exists")
    
    collections.get("cameras").insert_one({
        "cameraId": camera_data.cameraId,
        "location": camera_data.location,
        "cameraType": camera_data.cameraType,
        "createdAt": datetime.datetime.now(datetime.timezone.utc)
    })
    return {"status": "success", "message": "Camera added successfully."}

# Route to log an entry or exit event
@router.post("/log_event", status_code=status.HTTP_200_OK)
async def log_event(log_data : data_schemas.LogEvent, response : Response):
    
    # Verify camera exists
    camera = collections.get("cameras").find_one({"cameraId": log_data.cameraId})
    if not camera:
        response.status_code = status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Camera not found.")
    
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    
    # Insert the event in the EntryExitLogs collection
    collections.get("entry_exit_logs").insert_one({
        "name": log_data.name ,
        "createdAt": timestamp,
        "cameraId": log_data.cameraId,
        "type": log_data.type
    })

    # Trigger the real-time broadcast after logging the event
    await broadcast_analysis()
    
    return {"status": "success", "message": "Event logged successfully."}