from pydantic import BaseModel
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
    cameraType : Literal["entry", "exit"]

class LogEvent(BaseModel): 
    cameraId : str 
    name: str | None
    type : Literal["known", "unknown"]