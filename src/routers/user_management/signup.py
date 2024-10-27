from fastapi import (
    status,
    APIRouter,
    Response,
    HTTPException,
    Form,
    File,
    UploadFile,
    Depends,
)
from bson import ObjectId
from icecream import ic
from typing_extensions import Dict
from pymongo.collection import Collection
from db.db_models import create_models
from pydantic import ValidationError
import datetime
from utils.jwt_helper import get_current_user
from constants.constants import roles
from src.schemas import data_schemas
from utils import passwords_helper

# from logging import Logger
router = APIRouter(tags=["user-management"], prefix="/account/register")
collections: Dict[str, Collection] = create_models()


@router.post("/super-admin", status_code=status.HTTP_201_CREATED)
async def signup(
    response: Response,
    companyName: str = Form(...),
    email: str = Form(...),
    termsConditions: bool = Form(...),
    companyLogo: UploadFile = File(...),  # Company logo as file
    token: str = Depends(get_current_user),
):
    try:
        user_data = {
            "userName": companyName,
            "email": email,
            # "password": password,
            # "confirmPassword": confirmPassword,
            "termsConditions": termsConditions,
        }
        try:
            user_data = data_schemas.RegisterSuperAdmin(
                companyName=companyName,
                email=email,
                # password=password,
                # confirmPassword=confirmPassword,
                termsConditions=termsConditions,
            )
            user_data = user_data.model_dump()

        except ValidationError as exc_info:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=exc_info.errors()
            )
        if not collections.get("valid_tokens").find_one(
            {"access_uuid": token.get("jti")}
        ):
            response.status_code = status.HTTP_403_FORBIDDEN
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Token"
            )
        if token.get("role") != roles.master:
            response.status_code = status.HTTP_403_FORBIDDEN
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the necessary permissions to perform this action.",
            )

        if collections.get("accounts").find_one(filter={"email": email}):
            response.status_code = status.HTTP_409_CONFLICT
            return HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Company profile with given email {email} alread exists.",
            )

        logo_binary = await companyLogo.read()

        auto_generate_password = passwords_helper.generate_password(length=8)
        user_data["password"] = passwords_helper.hash(auto_generate_password)

        user_data.update(
            {
                "role": roles.super_admin,
                "createdAt": datetime.datetime.now(datetime.timezone.utc),
                "updatedAt": datetime.datetime.now(datetime.timezone.utc),
                "active": True,
                "companyLogo": logo_binary,
            }
        )
        # Insert user data into database
        collections.get("accounts").insert_one(user_data)
        # TODO: Log - I
        response.status_code = status.HTTP_201_CREATED
        return {
            "detail": "Company profile created successfully",
            "status_code": response.status_code,
            "email": email,
            "password": auto_generate_password,
        }

    except Exception as ex:
        # TODO: Log - C {ex}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"internal server error {ex}",
        )


@router.post("/admin", status_code=status.HTTP_201_CREATED)
async def signup_admin(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    confirmPassword: str = Form(...),
    token: str = Depends(get_current_user),
):
    try:
        user_data = {
            "email": email,
            "password": password,
            "confirmPassword": confirmPassword,
        }

        try:
            user_data = data_schemas.RegisterAdmin(
                email=email,
                password=password,
                confirmPassword=confirmPassword,
            )
            user_data = user_data.model_dump()

        except ValidationError as exc_info:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=exc_info.errors()
            )

        if not collections.get("valid_tokens").find_one(
            {"access_uuid": token.get("jti")}
        ):
            response.status_code = status.HTTP_403_FORBIDDEN
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Token"
            )

        if token.get("role") != roles.super_admin:
            response.status_code = status.HTTP_403_FORBIDDEN
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the necessary permissions to perform this action.",
            )

        if collections.get("accounts").find_one(filter={"email": email}):
            response.status_code = status.HTTP_409_CONFLICT
            return HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Admin profile with given email {email} alread exists.",
            )
        

        # Get logo: 
        super_admin_details = collections.get("accounts").find_one(filter={"_id": ObjectId(token.get("sub"))})
        user_data["password"] = passwords_helper.hash(user_data.get("password"))
        user_data.pop("confirmPassword")
        user_data.update(
            {
                "role": roles.admin,
                "companyLogo" : super_admin_details.get("companyLogo"),
                "createdAt": datetime.datetime.now(datetime.timezone.utc),
                "updatedAt": datetime.datetime.now(datetime.timezone.utc),
                "active": True,
            }
        )
        # Insert user data into database
        collections.get("accounts").insert_one(user_data)
        # Token generation for sending email to verify the user email
        # TODO: Log - I
        response.status_code = status.HTTP_201_CREATED
        return {
            "detail": "Admin profile created successfully.",
            "email": email,
            "password": password,
            "status_code": response.status_code,
        }

    except Exception as ex:
        # TODO: Log - C {ex}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"internal server error {ex}",
        )


@router.post("/user", status_code=status.HTTP_201_CREATED)
async def signup_user(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    confirmPassword: str = Form(...),
    token: str = Depends(get_current_user),
):
    try:
        user_data = {
            "email": email,
            "password": password,
            "confirmPassword": confirmPassword,
        }
        try:
            user_data = data_schemas.RegisterUser(
                email=email,
                password=password,
                confirmPassword=confirmPassword,
            )
            user_data = user_data.model_dump()

        except ValidationError as exc_info:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=exc_info.errors()
            )

        if not collections.get("valid_tokens").find_one(
            {"access_uuid": token.get("jti")}
        ):
            response.status_code = status.HTTP_403_FORBIDDEN
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Token"
            )

        if token.get("role") not in [roles.super_admin, roles.admin]:
            response.status_code = status.HTTP_403_FORBIDDEN
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the necessary permissions to perform this action.",
            )

        if collections.get("accounts").find_one(filter={"email": email}):
            response.status_code = status.HTTP_409_CONFLICT
            return HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User profile with given email {email} alread exists.",
            )
        

        # Get logo: 
        admin_details = collections.get("accounts").find_one(filter={"_id": ObjectId(token.get("sub"))})
        user_data["password"] = passwords_helper.hash(user_data.get("password"))
        user_data.pop("confirmPassword")
        user_data.update(
            {
                "role": roles.user,
                "companyLogo" : admin_details.get("companyLogo"),
                "createdAt": datetime.datetime.now(datetime.timezone.utc),
                "updatedAt": datetime.datetime.now(datetime.timezone.utc),
                "active": True,
            }
        )
        # Insert user data into database
        collections.get("accounts").insert_one(user_data)
        # Token generation for sending email to verify the user email
        # TODO: Log - I
        response.status_code = status.HTTP_201_CREATED
        return {
            "detail": "User profile created successfully.",
            "email": email,
            "password": password,
            "status_code": response.status_code,
        }

    except Exception as ex:
        # TODO: Log - C {ex}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"internal server error {ex}",
        )
