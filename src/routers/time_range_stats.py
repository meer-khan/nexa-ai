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
from src.analysis.log_entry_exit_helper import count_people_by_location
from src.schemas.data_schemas import CountPeople
app = FastAPI()

# MongoDB connection
router = APIRouter(tags=["timerange-stats"], prefix="/timerange-location-stats")
collections: Dict[str,Collection] = create_models()

# # Helper function to convert PST time to UTC
# def convert_pst_to_utc(pst_time_str: str) -> datetime:
#     pst = pytz.timezone('Asia/Karachi')
#     local_time = pst.localize(datetime.datetime.strptime(pst_time_str, "%Y-%m-%d %H:%M:%S"))
#     utc_time = local_time.astimezone(pytz.utc)
#     return utc_time




# API to get the count of people detected at a specific location within a time range
@router.get("/count_people_by_location")
async def count_people(time_range: CountPeople):
    try:
        # Define Pakistan Standard Time (PST)
        pst = pytz.timezone("Asia/Karachi")
        
        # Convert start_time and end_time from PST to UTC
        start_time_utc = pst.localize(time_range.start_time).astimezone(pytz.utc)
        end_time_utc = pst.localize(time_range.end_time).astimezone(pytz.utc)
        
        # Get the count of people detected at the specified location
        count = count_people_by_location(time_range.location, start_time_utc, end_time_utc)
        
        return {"location": time_range.location, "people_detected": count, "start_time_utc": time_range.start_time, "end_time_utc": time_range.end_time}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))