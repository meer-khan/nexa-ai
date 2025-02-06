from fastapi import (
    Form,
    HTTPException,
    APIRouter,
    UploadFile,
    File,
    Depends,
    Response,
    status,
)
from utils.jwt_helper import get_current_user
from constants.constants import roles
from pymongo.collection import Collection
from db.db_models import create_models
from typing_extensions import Dict
from utils import time_utilities
import pathlib
import datetime
import os
import io
import pandas as pd

router = APIRouter(tags=["entry-exit-logs"], prefix="/employees")
collections: Dict[str, Collection] = create_models()

#     return {"details": f"Employee Added Successfully. ID: {employeeID}"}
UPLOADS = r"D:/Uploads"
os.makedirs(UPLOADS, exist_ok=True)



@router.post("/upload-excel/")
async def upload_file(
    response: Response,
    file: UploadFile = File(...),
    token: dict = Depends(get_current_user),
):
    # Validate role
    if token.get("role") not in [roles["admin"], roles["super_admin"]]:
        response.status_code = status.HTTP_403_FORBIDDEN
        raise HTTPException(
            status_code=403,
            detail="You do not have necessary permissions",
        )

    # Check file extension
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an .xlsx file.")

    # Read Excel file
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents), dtype=str)  # Ensure all columns are string

    # Expected columns in Excel file
    expected_columns = {
        "Emp.ID": "employeeID",
        "Name": "name",
        "Employee Class": "employeeClass",
        "CNIC": "cnic",
        "Contact Number": "contactNumber",
        "Company": "company",
        "Category": "category",
        "Department": "department",
        "Sub Machine": "subMachine",
    }

    # Validate columns
    if not set(expected_columns.keys()).issubset(df.columns):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Missing required columns: {set(expected_columns.keys()) - set(df.columns)}",
        )

    # Rename columns to camelCase
    df.rename(columns=expected_columns, inplace=True)

    # Convert all data to string
    df = df.astype(str)

    # Convert DataFrame to dictionary records
    employees = df.to_dict(orient="records")

    # Fetch existing employee IDs
    existing_ids = set(
        doc["employeeID"] for doc in collections.get("employees").find({}, {"_id": 0, "employeeID": 1})
    )

    # Filter new employees (skip existing ones)
    new_employees = [emp for emp in employees if emp["employeeID"] not in existing_ids]

    # Insert only new employees
    if new_employees:
        collections.get("employees").insert_many(new_employees)

    response.status_code = status.HTTP_201_CREATED
    return {
        "message": f"File processed successfully. {len(new_employees)} new employees added.",
        "status_code": response.status_code,
    }


def validate_and_parse_date(date_str: str) -> datetime:
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use YYYY-MM-DD."
        )

# TODO: Refine query params , add variable name as well in query param 
@router.get("/logs/")
async def get_entry_exit_logs(
    response: Response,
    start_date: str ,
    end_date: str ,
    token: str = Depends(get_current_user),
):
    try:
        if token.get("role") not in [roles.admin, roles.super_admin, roles.user]:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return HTTPException(
                status_code=response.status_code,
                detail="You donot have necessary permissions",
            )
        # Convert input dates (assumed local) to UTC
        start_date_pst = validate_and_parse_date(start_date)
        end_date_pst = validate_and_parse_date(end_date)

        # Convert PST input to UTC for querying
        start_date_utc = time_utilities.convert_pst_to_utc(start_date_pst)
        end_date_utc = time_utilities.convert_pst_to_utc(end_date_pst)

        # Aggregation pipeline
        pipeline = [
            {"$match": {"createdAt": {"$gte": start_date_utc, "$lte": end_date_utc}}},
            {
                "$lookup": {
                    "from": "cameras",
                    "localField": "cameraId",
                    "foreignField": "cameraId",
                    "as": "camera_info",
                }
            },
            {"$unwind": "$camera_info"},
            {
                "$project": {
                    "_id": 0,
                    "name": 1,
                    "employeeID": 1,
                    "cameraId": 1,
                    "cameraType": "$camera_info.cameraType",
                    "location": "$camera_info.location",
                    "createdAt": 1,
                }
            },
        ]

        logs = list(collections.get("entry_exit_logs").aggregate(pipeline))
        # Convert createdAt from UTC to PST
        # datetime.datetime.strftime


        def parse_created_at(created_at_str):
            try:
                # Try parsing with the expected format (ISO 8601 with 'T' and 'Z')
                return datetime.datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                # If that fails, try parsing without 'T' and 'Z'
                return datetime.datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S.%f")

        # Convert logs
        for log in logs:
            log["createdAt"] = (
                parse_created_at(str(log["createdAt"]))
                .replace(tzinfo=datetime.timezone.utc)
                .isoformat()
            )

        return logs

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register")
async def register_employee(
    response: Response,
    name: str = Form(...),
    employeeID: str = Form(...),
    cnic: str = Form(None),  
    contactNumber: str = Form(None),  
    company: str = Form(None),  
    category: str = Form(None),  
    department: str = Form(None), 
    submachine: str = Form(None), 
    employeeClass: str = Form(None), 
    picture: UploadFile = File(...),
    token: str = Depends(get_current_user),
):
    # Validate role
    if token.get("role") not in [roles.admin, roles.super_admin]:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return HTTPException(
            status_code=response.status_code,
            detail="You donot have necessary permissions",
        )

    # Check if employeeID already exists in database
    if collections.get("employees").find_one({"employeeID": employeeID}):
        raise HTTPException(status_code=400, detail="EmployeeID already exists.")

    # Save the uploaded picture to a local directory
    # Preserve the file extension of the uploaded image
    file_extension = picture.filename.split(".")[-1]
    file_location = os.path.join(UPLOADS, f"{name}_{employeeID}.{file_extension}")
    file_location = pathlib.Path(file_location).as_posix()

    # Save the file
    with open(file_location, "wb") as f:
        f.write(await picture.read())

    # Save the employee data to the database
    new_employee = {
        "name": name,
        "employeeID": employeeID,
        "cnic": cnic,
        "contactNumber": contactNumber, 
        "company": company,
        "category": category,
        "department": department,
        "submachine":submachine, 
        "employeeClass":employeeClass,
        "profile_picture": file_location,  # Store the file path in the database
    }

    collections.get("employees").insert_one(new_employee)

    return {"details": f"Employee Added Successfully. ID: {employeeID}"}

@router.put("/{employeeID}")
async def update_employee(
    employeeID: str,
    response: Response,
    name: str = Form(None),
    cnic: str = Form(None),  
    contactNumber: str = Form(None),  
    company: str = Form(None),  
    category: str = Form(None),  
    department: str = Form(None), 
    submachine: str = Form(None), 
    employeeClass: str = Form(None), 
    picture: UploadFile = File(None),  # Optional picture update
    token: dict = Depends(get_current_user),
):
    # Validate role
    if token.get("role") not in [roles.admin, roles.super_admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the necessary permissions",
        )

    # Check if employee exists
    employee = collections.get("employees").find_one({"employeeID": employeeID})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found.")

    update_data = {}

    # Add fields to update if provided
    if name:
        update_data["name"] = name
    if cnic:
        update_data["cnic"] = cnic
    if contactNumber:
        update_data["contactNumber"] = contactNumber
    if company:
        update_data["company"] = company
    if category:
        update_data["category"] = category
    if department:
        update_data["department"] = department
    if submachine:
        update_data["submachine"] = submachine
    if employeeClass:
        update_data["employeeClass"] = employeeClass

    # Handle profile picture update
    if picture:
        file_extension = picture.filename.split(".")[-1]
        file_location = os.path.join(UPLOADS, f"{name or employee['name']}_{employeeID}.{file_extension}")
        file_location = pathlib.Path(file_location).as_posix()

        # Save the new picture
        with open(file_location, "wb") as f:
            f.write(await picture.read())

        # Add the file path to update_data
        update_data["profile_picture"] = file_location

    # Update employee data in the database
    if update_data:
        collections.get("employees").update_one(
            {"employeeID": employeeID}, {"$set": update_data}
        )
        return {"details": f"Employee {employeeID} updated successfully."}

    return {"details": "No updates were made."}



# GET API to fetch all registered employees
@router.get("/all")
async def get_employees(response: Response, token: str = Depends(get_current_user)):
    # Validate role
    if token.get("role") not in [roles.admin, roles.super_admin]:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return HTTPException(
            status_code=response.status_code,
            detail="You donot have necessary permissions",
        )

    # Get all employees from MongoDB
    employees = list(
        collections.get("employees").find({}, {"_id": 0})
    )  # Exclude MongoDB's internal _id field
    return employees


@router.delete("/delete/{employeeID}")
async def delete_employee(
    employeeID: str, response: Response, token: str = Depends(get_current_user)
):
    # Validate role
    if token.get("role") not in [roles.admin, roles.super_admin]:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return HTTPException(
            status_code=response.status_code,
            detail="You donot have necessary permissions",
        )

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
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to delete the profile picture: {str(e)}",
                )

    return {"details": "Employee and profile picture successfully deleted."}
