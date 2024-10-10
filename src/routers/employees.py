from fastapi import  Form, HTTPException, APIRouter , UploadFile, File
from pymongo.collection import Collection
from db.db_models import create_models
from typing_extensions import Dict
import os 

router = APIRouter(tags=["entry-exit-logs"], prefix="/employees")
collections: Dict[str, Collection] = create_models()

#     return {"details": f"Employee Added Successfully. ID: {employeeID}"}
UPLOADS = r"D:\Uploads"
os.makedirs(UPLOADS, exist_ok=True)

@router.post("/register")
async def register_employee(
    name: str = Form(...), 
    employeeID: str = Form(...),
    picture: UploadFile = File(...)
):
    # Check if employeeID already exists
    if collections.get("employees").find_one({"employeeID": employeeID}):
        raise HTTPException(status_code=400, detail="EmployeeID already exists.")

    # Save the uploaded picture to a local directory
    # Preserve the file extension of the uploaded image
    file_extension = picture.filename.split('.')[-1]
    file_location = os.path.join(UPLOADS, f"{name}_{employeeID}.{file_extension}")
    
    # Save the file
    with open(file_location, "wb") as f:
        f.write(await picture.read())

    # Save the employee data to the database
    new_employee = {
        "name": name,
        "employeeID": employeeID,
        "profile_picture": file_location,  # Store the file path in the database
    }
    
    collections.get("employees").insert_one(new_employee)

    return {"details": f"Employee Added Successfully. ID: {employeeID}"}

# GET API to fetch all registered employees
@router.get("/all")
async def get_employees():
    # Get all employees from MongoDB
    employees = list(collections.get("employees").find({}, {"_id": 0}))  # Exclude MongoDB's internal _id field
    return employees


@router.delete("/delete/{employeeID}")
async def delete_employee(employeeID: str):
    # Fetch the employee data to get the profile picture path
    employee = collections.get("employees").find_one({"employeeID": employeeID})
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found.")
    
    # Delete the employee from MongoDB
    result = collections.get("employees").delete_one({"employeeID": employeeID})

    # If the deletion was successful, try to delete the corresponding profile picture
    if result.deleted_count > 0:
        profile_picture_path = employee.get("profile_picture")
        
        # Check if the profile picture path exists and delete the file
        if profile_picture_path and os.path.exists(profile_picture_path):
            try:
                os.remove(profile_picture_path)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to delete the profile picture: {str(e)}")

    return {"details": "Employee and profile picture successfully deleted."}