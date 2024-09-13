from fastapi import FastAPI, HTTPException
from fastapi import (
    APIRouter,
    HTTPException,
)
from pymongo.collection import Collection
from typing_extensions import Dict
from db.db_models import create_models
import pytz
from src.schemas.data_schemas import CountPeople
import datetime
app = FastAPI()

# MongoDB connection
router = APIRouter(tags=["timerange-stats"], prefix="/timerange-location-stats")
collections: Dict[str,Collection] = create_models()


# Define Pakistan Standard Time (PST) timezone
pst = pytz.timezone('Asia/Karachi')

# Convert PST time to UTC
def convert_pst_to_utc(pst_time: datetime) -> datetime:
    pst_localized = pst.localize(pst_time)
    return pst_localized.astimezone(datetime.timezone.utc)

def count_people_in_time_range(start_time_pst: datetime, end_time_pst: datetime):
    # Convert the PST times to UTC
    start_time_utc = convert_pst_to_utc(start_time_pst)
    end_time_utc = convert_pst_to_utc(end_time_pst)

    # Get all camera IDs of entry and exit types
    entry_camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"cameraType": "entry"})]
    exit_camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"cameraType": "exit"})]

    # Get all records of people who entered the factory but did not exit till the start time
    entries_before_start_time = collections.get("entry_exit_logs").find({
        "cameraId": {"$in": entry_camera_ids},
        "createdAt": {"$lte": start_time_utc},
        "type": "entry"
    })

    exits_before_start_time = collections.get("entry_exit_logs").find({
        "cameraId": {"$in": exit_camera_ids},
        "createdAt": {"$lte": start_time_utc},
        "type": "exit"
    })

    # Find people who entered but haven't exited
    entry_ids = {entry["personId"] for entry in entries_before_start_time}
    exit_ids = {exit["personId"] for exit in exits_before_start_time}
    people_still_in_factory = list(entry_ids - exit_ids)

    # Get all workers detected on 'assembly_line' cameras within the specified time range
    assembly_line_camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"cameraType": "assembly_line"})]
    
    workers_on_assembly_line = collections.get("entry_exit_logs").find({
        "cameraId": {"$in": assembly_line_camera_ids},
        "createdAt": {"$gte": start_time_utc, "$lte": end_time_utc}
    })

    # Compile the results
    result = {
        "people_still_in_factory": people_still_in_factory,
        "workers_on_assembly_line": list(workers_on_assembly_line)
    }

    return result


# API to get the count of people detected at a specific location within a time range
@router.get("/time-range-stats")
async def count_people(time_range: CountPeople):
    try:
        # Define Pakistan Standard Time (PST)
        pst = pytz.timezone("Asia/Karachi")
        
        # Convert start_time and end_time from PST to UTC
        start_time_utc = pst.localize(time_range.start_time).astimezone(pytz.utc)
        end_time_utc = pst.localize(time_range.end_time).astimezone(pytz.utc)
        
        # Get the count of people detected at the specified location
        count = count_people_in_time_range(time_range.location, start_time_utc, end_time_utc)
        
        return {"location": time_range.location, "people_detected": count, "start_time_utc": time_range.start_time, "end_time_utc": time_range.end_time}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))