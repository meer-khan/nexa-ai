from fastapi import HTTPException
from fastapi import (
    APIRouter,
    HTTPException,
)
from pymongo.collection import Collection
from typing_extensions import Dict
from db.db_models import create_models
from src.schemas.data_schemas import CountPeople
from utils.time_utilities import convert_pst_to_utc
import datetime

# MongoDB connection
router = APIRouter(tags=["timerange-stats"], prefix="/stats")
collections: Dict[str, Collection] = create_models()


def count_people_in_time_range(start_time_pst: datetime, end_time_pst: datetime):
    # Convert the PST times to UTC
    start_time_utc = convert_pst_to_utc(start_time_pst)
    end_time_utc = convert_pst_to_utc(end_time_pst)
    
    # Get all camera IDs of entry and exit types
    entry_camera_ids = [
        cam["cameraId"]
        for cam in collections.get("cameras").find({"cameraType": "entry"})
    ]
    exit_camera_ids = [
        cam["cameraId"]
        for cam in collections.get("cameras").find({"cameraType": "exit"})
    ]
    
    # Get all records of people who entered the factory but did not exit by the start time
    entries_before_start_time = list(collections.get("entry_exit_logs").find(
        {
            "cameraId": {"$in": entry_camera_ids},
            "createdAt": {"$lte": start_time_utc},
        }
    ))

    exits_before_end_time = list(collections.get("entry_exit_logs").find(
        {
            "cameraId": {"$in": exit_camera_ids},
            "createdAt": {"$lte": end_time_utc},
        }
    ))

    # Pairing entries and exits based on employeeID and time
    entry_data = {
        entry["employeeID"]: {
            "name": entry.get("name", "Unknown"), 
            "cameraId": entry.get("cameraId", "Unknown"), 
            "employeeID": entry.get("employeeID"), 
            "type": entry.get("type", "unknown"),
            "createdAt": entry["createdAt"]  # Keep createdAt for comparison
        }
        for entry in entries_before_start_time
    }
    
    exit_ids = {exit["employeeID"]: exit["createdAt"] for exit in exits_before_end_time}

    # Find people who entered but haven't exited
    people_still_in_factory = [
        entry_data[emp_id] for emp_id, entry_time in entry_data.items()
        if emp_id not in exit_ids or entry_time["createdAt"] > exit_ids[emp_id]
    ]

    for peo in people_still_in_factory:
        peo.pop("createdAt")
    

    # Get all workers detected on 'assembly_line' cameras within the specified time range
    assembly_line_camera_ids = [
        cam["cameraId"]
        for cam in collections.get("cameras").find({"cameraType": "assembly_line"})
    ]

    workers_on_assembly_line = list(collections.get("entry_exit_logs").find(
        {
            "cameraId": {"$in": assembly_line_camera_ids},
            "createdAt": {"$gte": start_time_utc, "$lte": end_time_utc},
        },
        {"_id": 0, "createdAt": 0},
    ))

    result = {
        "people_still_in_factory": people_still_in_factory,
        "workers_on_assembly_line": workers_on_assembly_line,
    }

    return result



# API to get the count of people detected at a specific location within a time range
@router.post("/time-range-stats")
async def count_people(time_range: CountPeople):
    try:
        results = count_people_in_time_range(
            start_time_pst=time_range.start_time, end_time_pst=time_range.end_time
        )
        return {"details": results}
    except Exception as e:
        raise e
        raise HTTPException(status_code=500, detail=str(e))
