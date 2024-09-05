from fastapi import APIRouter, HTTPException, status, Response
from pymongo.collection import Collection
from src.schemas import data_schemas
from db.db_models import create_models
from icecream import ic
import datetime
# from

router = APIRouter(tags=["entry-exit-logs"], prefix="/cameras")
collections = create_models()



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
    
    return {"status": "success", "message": "Event logged successfully."}

# # Route to get count of people inside the building and assembly line area
# @router.get("/current_count/")
# async def get_current_count():
#     # Aggregate to find the current count of people in each area
#     pipeline = [
#         {"$lookup": {
#             "from": "Cameras",
#             "localField": "camera_id",
#             "foreignField": "camera_id",
#             "as": "camera_info"
#         }},
#         {"$unwind": "$camera_info"},
#         {"$group": {
#             "_id": "$camera_info.location",
#             "entries": {"$sum": {"$cond": [{"$eq": ["$event_type", "entry"]}, 1, 0]}},
#             "exits": {"$sum": {"$cond": [{"$eq": ["$event_type", "exit"]}, 1, 0]}}
#         }},
#         {"$project": {
#             "location": "$_id",
#             "current_count": {"$subtract": ["$entries", "$exits"]}
#         }}
#     ]
    
#     result = list(entry_exit_logs.aggregate(pipeline))
#     return {"status": "success", "data": result}

# # Route to get count of people who entered and left in the last 24 hours
# @router.get("/last_24_hours_count/")
# async def last_24_hours_count():
#     now = datetime.utcnow()
#     last_24_hours = now - timedelta(hours=24)
    
#     pipeline = [
#         {"$match": {"timestamp": {"$gte": last_24_hours}}},
#         {"$group": {
#             "_id": "$event_type",
#             "count": {"$sum": 1}
#         }}
#     ]
    
#     result = list(entry_exit_logs.aggregate(pipeline))
#     return {"status": "success", "data": result}