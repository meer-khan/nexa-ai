from fastapi import APIRouter, HTTPException, status
from pymongo.collection import Collection
from src.schemas import data_schemas
from db.db_models import create_models
from icecream import ic
import datetime
# from

router = APIRouter(tags=["person-detection"], prefix="/person-detection")
collections = create_models()

@router.post("/person", status_code=status.HTTP_201_CREATED)
async def post_person_identification(person: data_schemas.PersonIdentification):
    pi: Collection = collections.get("pi")
    
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
    
    # If no documents are found, raise a 404 error
    if not people:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No records found"
        )
    
    # Optionally, transform the '_id' field to 'id' if needed
    for peo in people:
        peo["id"] = str(peo.pop("_id"))
    return people