from pydantic import BaseModel

class ActivityDetected(BaseModel): 
    intrustionClass: str
    cameraId: str

class PersonIdentification(BaseModel):
    personId: str
    personName: str
    location: str

