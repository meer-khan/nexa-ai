from fastapi import APIRouter, HTTPException, status
from pymongo.collection import Collection
from src.schemas import data_schemas
from db.db_models import create_models
import datetime

router = APIRouter(tags=["person-detection"], prefix="/person-detection")
collections = create_models()

@router.post("/person", status_code=status.HTTP_201_CREATED)
async def post_person_identification(person: data_schemas.PersonIdentification):
    pi: Collection = collections.get("pi")
    
    created_at = datetime.datetime.now(datetime.timezone.utc)

    last_entry = pi.find_one(sort=[("createdAt", -1)])
    
    if last_entry:
        last_created_at = last_entry["createdAt"]
        time_diff = created_at  - last_created_at.replace(tzinfo=datetime.timezone.utc)
        
        if time_diff < datetime.timedelta(seconds=10):
            return {"details": "Data received but not added to the database due to the 10-second rule."}
        
    person_dict = person.model_dump()
    created_at = datetime.datetime.now(datetime.timezone.utc)
    person_dict.update({"createdAt": created_at})
    pi.insert_one(person_dict)
    return {"detail": "Person added successfully"}

# GET API to fetch all persons (for verification)
@router.get("/person")
async def get_people_identification():
    pi: Collection = collections.get("pi")
    people = list(pi.find())

    if not people:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No records found"
        )
    
    for peo in people:
        peo["id"] = str(peo.pop("_id"))
    return people