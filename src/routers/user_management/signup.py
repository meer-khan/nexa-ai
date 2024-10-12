from fastapi import status, APIRouter, Response, HTTPException, Form, File, UploadFile, Depends
from icecream import ic
from typing_extensions import Dict
from pymongo.collection import Collection
from db.db_models import create_models
from pydantic import ValidationError
import datetime
from utils.jwt_helper import verify_token, get_current_user
from constants.constants import roles
from src.schemas import data_schemas
from utils import hash_helper

router = APIRouter(tags=["user-management"], prefix="/account")
collections: Dict[str, Collection] = create_models()


@router.post("/super-admin/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    response: Response,
    companyName: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirmPassword: str = Form(...),
    termsConditions: bool = Form(...),
    companyLogo: UploadFile = File(...),  # Company logo as file
    token: str = Depends(get_current_user)
):
    try:
        user_data = {
            "userName": companyName,
            "email": email,
            "password": password,
            "confirmPassword": confirmPassword,
            "termsConditions": termsConditions
        }
        try:
            user_data = data_schemas.Signup(
                companyName=companyName,
                email=email,
                password=password,
                confirmPassword=confirmPassword,
                termsConditions=termsConditions,
            )
            user_data = user_data.model_dump()
            
        except ValidationError as exc_info:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=exc_info.errors()
            )
        if token.get("role") != "master":
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the necessary permissions to perform this action."
            )
        
        if collections.get("accounts").find_one(filter={"email": email}):
            response.status_code = status.HTTP_409_CONFLICT
            return HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Company profile with given email {email} alread exists."
            )

        # user_data.update({"companyLogo": companyLogo})
        # Read and store the company logo
        logo_binary = await companyLogo.read()
        # check_email_exists = collections.get("accounts").find_one({"email": user_data.get("email")})

        user_data["password"] = hash_helper.hash(user_data.get("password"))
        user_data.pop("confirmPassword")
        user_data.update(
            {
                "roles":roles.super_admin ,
                "createdAt": datetime.datetime.now(datetime.timezone.utc),
                "updatedAt": datetime.datetime.now(datetime.timezone.utc),
                "active": True, 
                "companyLogo": logo_binary
            }
        )
        # Insert user data into database
        id = collections.get("accounts").insert_one(user_data)
        ic(id.inserted_id)
        # Token generation for sending email to verify the user email
        # TODO: Log - I
        response.status_code = status.HTTP_201_CREATED
        return {"detail": "Company profile created successfully", "status_code": response.status_code}

    except Exception as ex:
        # TODO: Log - C {ex}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"internal server error {ex}",
        )
