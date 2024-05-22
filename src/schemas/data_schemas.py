from pydantic import BaseModel

class ActivityDetected(BaseModel): 
    intrustionClass: str
    cameraId: str

class PersonIdentification(BaseModel):
    person_id: int
    person_name: str
    location: str

