from pydantic import BaseModel
import datetime
from typing_extensions import Literal
class ActivityDetected(BaseModel): 
    intrustionClass: str
    cameraId: str

class PersonIdentification(BaseModel):
    personId: str
    personName: str
    location: str

class AddCamera(BaseModel): 
    cameraId: str
    location:str
    cameraType : Literal["entry", "exit", "inside"]

class LogEvent(BaseModel): 
    cameraId : str 
    name: str | None
    type : Literal["known", "unknown"]


# Pydantic model for the request body
class CountPeople(BaseModel):
    start_time: datetime.datetime  # No timezone info; expected to be in PST
    end_time: datetime.datetime    # No timezone info; expected to be in PST
    location: str