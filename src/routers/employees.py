from fastapi import  Form, HTTPException, APIRouter
from pymongo.collection import Collection
from db.db_models import create_models
from typing_extensions import Dict
from fastapi.responses import JSONResponse


router = APIRouter(tags=["entry-exit-logs"], prefix="/cameras")
collections: Dict[str, Collection] = create_models()

# In-memory storage for employees (use a database in production)
employees_db = []
@router.post("/register-employee/")
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

    return JSONResponse(content={"message": "Employee registered successfully", "employee": new_employee})

# GET API to fetch all registered employees
@router.get("/employees/")
async def get_employees():
    # Get all employees from MongoDB
    employees = list(collections.get("employees").find({}, {"_id": 0}))  # Exclude MongoDB's internal _id field
    return employees
