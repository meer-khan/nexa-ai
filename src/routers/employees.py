from fastapi import  Form, HTTPException, APIRouter
from pymongo.collection import Collection
from db.db_models import create_models
from typing_extensions import Dict

router = APIRouter(tags=["entry-exit-logs"], prefix="/employees")
collections: Dict[str, Collection] = create_models()

@router.post("/register")
async def register_employee(
    name: str = Form(...), 
    employeeID: str = Form(...)
):
    if collections.get("employees").find_one({"employeeID": employeeID}):
        raise HTTPException(status_code=400, detail="EmployeeID already exists.")

    new_employee = {
        "name": name,
        "employeeID": employeeID,
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
    # Check if employeeID exists in MongoDB
    result = collections.get("employees").delete_one({"employeeID": employeeID})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found.")

    return {"details": "successfully deleted the employee"}