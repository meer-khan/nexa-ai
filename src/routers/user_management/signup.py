from fastapi import status, APIRouter, Response, HTTPException, Form
from icecream import ic
from pydantic import ValidationError
import datetime
from datetime import timedelta
from schemas import data_schemas
import app
from utils import jwt_helper
from utils import hash_helper

router = APIRouter(tags=["user-management"], prefix="/user")



@router.post("/super-admin/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    response: Response,
    userName: str = Form(...),
    email: str = Form(...),
    password1: str = Form(...),
    password2: str = Form(...),
    termsConditions: bool = Form(...),
):
    try:
        user_data = {
            "userName": userName,
            "email": email,
            "password1": password1,
            "password2": password2,
            "termsConditions": termsConditions
        }
        try:
            user_data = data_schemas.Signup(
                userName=userName,
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

        check_email_exists = app.col_user.find_one({"email": user_data.get("email")})

        # If user exists, send email to the existing account
        if check_email_exists:
            if not check_email_exists.get("active"):
                access_token, _, _ = jwt_helper.create_access_token(
                    {
                        "sub": str(check_email_exists.get("_id")),
                        "ver": check_email_exists.get("passVer"),
                    }
                )
                response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
                return {
                    "detail": "Your account already exists but not verified, check your email to verify it",
                    "status_code": response.status_code,
                }

            else:
                response.status_code = status.HTTP_409_CONFLICT
                return {
                    "detail": " Your account already exists and verified, Go to login",
                    "status_code": response.status_code,
                }

        user_data["password"] = hash_helper.hash(user_data["password1"])
        user_data.pop("password1")
        user_data.pop("password2")
        query_dict = {"plan_id": 0}
        plan_id = str(app.col_plan.find_one(query_dict).get("_id"))
        # plan_id = db_query.find_single_record(collection=app.col_plan ,data_dict= query_dict ).get("_id")
        plan_end_date = datetime.datetime.now(datetime.timezone.utc) + timedelta(
            days=30
        )
        ic(plan_id)
        user_data.update(
            {
                "roles": ["user"],
                "plan": plan_id,
                "planEndAt": plan_end_date,
                "createdAt": datetime.datetime.now(datetime.timezone.utc),
                "updatedAt": datetime.datetime.now(datetime.timezone.utc),
                "active": False,
                "passVer": 1,
            }
        )
        # Insert user data into database
        inserted_id = app.col_user.insert_one(user_data)
        ic(inserted_id.inserted_id)

        # Token generation for sending email to verify the user email
        access_token, access_jti, access_exp = jwt_helper.create_access_token(
            {"sub": str(inserted_id.inserted_id), "ver": user_data.get("passVer")}
        )

        # SEND EMAIL TO THE USER TO VERIFY THE ACCOUNT

        # TODO: Log - I
        return {"detail": "user registered successfully", "status_code": response.status_code}

    except Exception as ex:
        # TODO: Log - C {ex}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"internal server error {ex}",
        )
