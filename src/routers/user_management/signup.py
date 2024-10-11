from fastapi import status, APIRouter, Response, HTTPException, Form
from icecream import ic
from typing_extensions import Dict, List
from pymongo.collection import Collection
from db.db_models import create_models
from pydantic import ValidationError
import datetime
from constants.constants import roles
from schemas import data_schemas
import app
from utils import jwt_helper
from utils import hash_helper

router = APIRouter(tags=["user-management"], prefix="/account")
collections: Dict[str, Collection] = create_models()


@router.post("/super-admin/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    response: Response,
    companyName: str = Form(...),
    email: str = Form(...),
    password1: str = Form(...),
    password2: str = Form(...),
    termsConditions: bool = Form(...),
):
    try:
        user_data = {
            "userName": companyName,
            "email": email,
            "password1": password1,
            "password2": password2,
            "termsConditions": termsConditions
        }
        try:
            user_data = data_schemas.Signup(
                companyName=companyName,
                email=email,
                password1=password1,
                password2=password2,
                termsConditions=termsConditions,
            )
            user_data = user_data.model_dump()
        except ValidationError as exc_info:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=exc_info.errors()
            )

        check_email_exists = collections.get("accounts").find_one({"email": user_data.get("email")})

        # If user exists, send email to the existing account
        if not check_email_exists:
            response.status_code = status.HTTP_409_CONFLICT
            return {
                "detail": f"Your account against email address {email} already exists",
                "status_code": response.status_code,
            }

        user_data["password"] = hash_helper.hash(user_data["password1"])
        user_data.pop("password1")
        user_data.pop("password2")
        user_data.update(
            {
                "roles":roles.super_admin ,
                "createdAt": datetime.datetime.now(datetime.timezone.utc),
                "updatedAt": datetime.datetime.now(datetime.timezone.utc),
                "active": False,
            }
        )
        # Insert user data into database
        id = collections.get("accounts").insert_one(user_data)
        ic(id.inserted_id)
        # Token generation for sending email to verify the user email
        # TODO: Log - I
        return {"detail": "user registered successfully", "status_code": response.status_code}

    except Exception as ex:
        # TODO: Log - C {ex}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"internal server error {ex}",
        )
