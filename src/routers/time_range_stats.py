from fastapi import FastAPI, HTTPException
import datetime
from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Response,
    WebSocket,
    WebSocketDisconnect,
)
from pymongo.collection import Collection
from typing_extensions import Dict
from db.db_models import create_models
import pytz

app = FastAPI()

# MongoDB connection
router = APIRouter(tags=["timerange-stats"], prefix="/timerange-stats")
collections: Dict[str,Collection] = create_models()

# Helper function to convert PST time to UTC
def convert_pst_to_utc(pst_time_str: str) -> datetime:
    pst = pytz.timezone('Asia/Karachi')
    local_time = pst.localize(datetime.datetime.strptime(pst_time_str, "%Y-%m-%d %H:%M:%S"))
    utc_time = local_time.astimezone(pytz.utc)
    return utc_time

# HTTP API to get analysis based on time range in PST
@app.get("/api/analysis/")
async def get_analysis(start_time: str, end_time: str):
    try:
        # Convert PST to UTC
        start_time_utc = convert_pst_to_utc(start_time)
        end_time_utc = convert_pst_to_utc(end_time)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use 'YYYY-MM-DD HH:MM:SS'.")

    # Query the database
    entries = collections.get("entry_exit_logs").count_documents({"createdAt": {"$gte": start_time_utc, "$lte": end_time_utc}, "type": "entry"})
    exits = collections.get("entry_exit_logs").count_documents({"createdAt": {"$gte": start_time_utc, "$lte": end_time_utc}, "type": "exit"})

    # Get the number of people at each camera location
    location_people_count = {}
    camera_locations = collections.get("cameras").distinct("location")
    for location in camera_locations:
        camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"location": location})]
        location_entries = collections.get("entry_exit_logs").count_documents({"createdAt": {"$gte": start_time_utc, "$lte": end_time_utc}, "type": "entry", "cameraId": {"$in": camera_ids}})
        location_exits = collections.get("entry_exit_logs").count_documents({"createdAt": {"$gte": start_time_utc, "$lte": end_time_utc}, "type": "exit", "cameraId": {"$in": camera_ids}})
        location_people_count[location] = location_entries - location_exits

    # Return the results
    return {
        "entries": entries,
        "exits": exits,
        "people_by_location": location_people_count
    }
