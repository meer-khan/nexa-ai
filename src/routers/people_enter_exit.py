from fastapi import APIRouter, HTTPException, status, Response
from src.routers.intrusion_stats_ws import broadcast_analysis
from src.routers import last_hour_assembly_line_stats
from src.routers import todays_visits
from src.routers import within_building
from pymongo.collection import Collection
from typing_extensions import Dict
from src.schemas import data_schemas
from db.db_models import create_models
from datetime import datetime, timezone, timedelta
import pytz

router = APIRouter(tags=["entry-exit-logs"], prefix="/cameras")
collections: Dict[str, Collection] = create_models()


# Route to add a new camera
@router.post("/add", status_code=status.HTTP_200_OK)
async def add_camera(camera_data: data_schemas.AddCamera, response: Response):
    if collections.get("cameras").find_one({"cameraId": camera_data.cameraId}):
        response.status_code = status.HTTP_400_BAD_REQUEST
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Camera id already exists"
        )

    collections.get("cameras").insert_one(
        {
            "cameraId": camera_data.cameraId,
            "location": camera_data.location,
            "cameraType": camera_data.cameraType,
            "createdAt": datetime.datetime.now(datetime.timezone.utc),
        }
    )
    return {"status": "success", "message": "Camera added successfully."}


# # Route to log an entry or exit event
# @router.post("/log-event", status_code=status.HTTP_200_OK)
# async def log_event(log_data: data_schemas.LogEvent, response: Response):
#     # Verify camera exists
#     camera = collections.get("cameras").find_one({"cameraId": log_data.cameraId})
#     employee = collections.get("employees").find_one(
#         {"employeeID": log_data.employeeID}
#     )
#     if not camera or not employee:
#         response.status_code = status.HTTP_400_BAD_REQUEST
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Camera or Employee not found.",
#         )

#     timestamp = datetime.datetime.now(datetime.timezone.utc)

#     # Insert the event in the EntryExitLogs collection
#     collections.get("entry_exit_logs").insert_one(
#         {
#             "name": log_data.name,
#             "createdAt": timestamp,
#             "cameraId": log_data.cameraId,
#             "employeeID": log_data.employeeID,
#             "type": log_data.type,
#         }
#     )

#     # Trigger the real-time broadcast after logging the event
#     await broadcast_analysis()
#     await last_hour_assembly_line_stats.broadcast_analysis()
#     await todays_visits.broadcast_analysis()
#     await within_building.broadcast_analysis()
#     return {"status": "success", "message": "Event logged successfully."}

# Route to log an entry or exit event

@router.post("/log-event", status_code=status.HTTP_200_OK)
async def log_event(log_data: data_schemas.LogEvent, response: Response):
    # Verify camera exists
    camera = collections.get("cameras").find_one({"cameraId": log_data.cameraId})
    employee = collections.get("employees").find_one({"employeeID": log_data.employeeID})

    if not camera or not employee:
        response.status_code = status.HTTP_400_BAD_REQUEST
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Camera or Employee not found.",
        )

    # Current timestamp with timezone awareness (UTC)
    timestamp = datetime.now(timezone.utc)

    # Fetch the last log for the same employee
    last_log = collections.get("entry_exit_logs").find_one(
        {"employeeID": log_data.employeeID},
        sort=[("createdAt", -1)]
    )

    # If there is a last log and it's within 10 seconds, reject the new log
    if last_log:
        last_log_time = last_log["createdAt"]

        # Check if the last_log_time is naive, and if so, make it timezone-aware
        if last_log_time.tzinfo is None:
            last_log_time = last_log_time.replace(tzinfo=timezone.utc)

        # Calculate the time difference
        time_diff = timestamp - last_log_time
        if time_diff.total_seconds() <= 10:
            return {
                "status": "not added",
                "message": "Data received but not added to the database due to the 10-second rule."
            }

    # Insert the event in the EntryExitLogs collection
    collections.get("entry_exit_logs").insert_one(
        {
            "name": log_data.name,
            "createdAt": timestamp,
            "cameraId": log_data.cameraId,
            "employeeID": log_data.employeeID,
            "type": log_data.type,
        }
    )

    # Trigger the real-time broadcast after logging the event
    await broadcast_analysis()
    await last_hour_assembly_line_stats.broadcast_analysis()
    await todays_visits.broadcast_analysis()
    await within_building.broadcast_analysis()

    return {"status": "success", "message": "Event logged successfully."}


def convert_utc_to_pst(utc_time: datetime):
    pst_timezone = pytz.timezone("Asia/Karachi")  # Pakistan Standard Time
    return utc_time.astimezone(pst_timezone)

@router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_locations():
    cameras = []
    all_cameras = collections.get("cameras").find({}, {"_id": 0})
    for cam in all_cameras:
        if cam.get("createdAt"):
            registered_time = convert_utc_to_pst(cam.get("createdAt"))
            cameras.append(
                {
                    "cameraID": cam.get("cameraId"),
                    "cameraLocation": cam.get("location"),
                    "cameraRegisteredAt":registered_time,
                    "cameraType": cam.get("cameraType"),
                }
            )
    return {"cameras": cameras}
