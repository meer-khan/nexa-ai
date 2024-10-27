from fastapi import APIRouter, HTTPException, status
from pymongo.collection import Collection
from src.schemas import data_schemas
from db.db_models import create_models
import datetime

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



@router.get("/activity-detected")
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