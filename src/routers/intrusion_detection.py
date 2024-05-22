from fastapi import APIRouter, HTTPException, status
from pymongo.collection import Collection
from typing_extensions import List, Dict
from src.schemas import data_schemas
from db.db_models import create_models
from icecream import ic
import datetime
# from

router = APIRouter(tags=["intrusion-detection"], prefix="/intrusion-detection")
collections = create_models()


@router.post("/activity-detected", status_code=status.HTTP_201_CREATED)
async def post_activity_detected(data: data_schemas.ActivityDetected):
    cid: Collection = collections.get("cid")
    created_at = datetime.datetime.now(datetime.timezone.utc)

    last_entry = cid.find_one(sort=[("createdAt", -1)])
    
    if last_entry:
        last_created_at = last_entry["createdAt"]
        time_diff = created_at  - last_created_at.replace(tzinfo=datetime.timezone.utc)
        
        if time_diff < datetime.timedelta(seconds=20):
            return {"details": "Data received but not added to the database due to the 20-second rule."}
        
    cid.insert_one(
        document={
            "intrustionClass": data.intrustionClass,
            "cameraId": data.cameraId,
            "createdAt": created_at,
        }
    )

    return {"details": "record added successfully"}



@router.get("/activity-detected", response_model=List[data_schemas.ActivityDetected])
async def get_activity_data():
    cid: Collection = collections.get("cid")
    
    # Fetch all documents from the collection
    documents = list(cid.find())
    
    # If no documents are found, raise a 404 error
    if not documents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No records found"
        )
    
    # Optionally, transform the '_id' field to 'id' if needed
    for doc in documents:
        doc["id"] = str(doc.pop("_id"))
    
    return documents


@router.post("/add-person", status_code=status.HTTP_201_CREATED)
async def post_person_identification(person: data_schemas.PersonIdentification):
    pi: Collection = collections.get("pi")
    
    person_dict = person.model_dump()
    created_at = datetime.datetime.now(datetime.timezone.utc)
    person_dict.update({"createdAt": created_at})
    await pi.insert_one(person_dict)
    return {"detail": "Person added successfully"}

# GET API to fetch all persons (for verification)
@router.get("/people")
async def get_people_identification():
    pi: Collection = collections.get("pi")
    people = await pi.find()
    return people