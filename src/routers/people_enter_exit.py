from fastapi import APIRouter, HTTPException, status
from pymongo.collection import Collection
from src.schemas import data_schemas
from db.db_models import create_models
from icecream import ic
import datetime
# from

router = APIRouter(tags=["entry-exit-logs"], prefix="/cameras")
collections = create_models()



# Route to add a new camera
@router.post("/add_camera/")
async def add_camera(camera_id: str, location: str):
    collections.get("cameras").insert_one({
        "camera_id": camera_id,
        "location": location,
        "createdAt": datetime.datetime.now(datetime.UTC)
    })
    return {"status": "success", "message": "Camera added successfully."}

# Route to log an entry or exit event
@router.post("/log_event/")
async def log_event(person_id: str, camera_id: str, event_type: str):
    if event_type not in ["entry", "exit"]:
        raise HTTPException(status_code=400, detail="Invalid event_type. Must be 'entry' or 'exit'.")
    
    # Verify camera exists
    camera = collections.get("cameras").find_one({"camera_id": camera_id})
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found.")
    
    timestamp = datetime.datetime.now(datetime.UTC)
    
    # Insert the event in the EntryExitLogs collection
    collections.get("entry_exit_logs").insert_one({
        "person_id": person_id,
        "timestamp": timestamp,
        "camera_id": camera_id,
        "event_type": event_type
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