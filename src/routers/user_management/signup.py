from fastapi import status, APIRouter, Response, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
from icecream import ic
from pydantic import ValidationError
from bson import ObjectId
import datetime
from datetime import timedelta
from schemas import data_schemas
import app
import os
from utils import oauth
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from decouple import config
import smtplib
import pathlib
from utils import password_manager

router = APIRouter(tags=["user-management"], prefix="/user")


def link_generator(route: str, token: str):
    host = config("EMAIL_HOST")
    port = config("EMAIL_PORT")
    return f"http://{host}:{port}/{route}/?token={token}"


def send_email(
    token: str, subject: str, recipient_email: str, body_message: str, route: str
):
    # Your email credentials

    sender_email = config("EMAIL")
    sender_password = config("EMAIL_PASSWORD")

    # Create the MIME object
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject

    # Create body text
    link = link_generator(route=route, token=token)
    body_text = f"{body_message} --- {link}"
    msg.attach(MIMEText(body_text, "plain"))

    # Connect to the SMTP server and send the email
    # with smtplib.SMTP("smtp.office365.com", 587) as server:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        err = server.sendmail(sender_email, recipient_email, msg.as_string())
        # TODO: ERROR LOG


def get_template(html_file_name: str) -> str:
    template_path = os.path.join(
        str(pathlib.Path("__file__").resolve().parent),
        "templates",
        html_file_name,
    )
    with open(template_path, "r") as f:
        html_content = f.read()
    return html_content


@router.post("/signup", status_code=status.HTTP_201_CREATED)
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
            "termsConditions": termsConditions,
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
                access_token, _, _ = oauth.create_access_token(
                    {
                        "sub": str(check_email_exists.get("_id")),
                        "ver": check_email_exists.get("passVer"),
                    }
                )
                send_email(
                    token=access_token,
                    subject="Verify Account - HOMESETV",
                    recipient_email=user_data.get("email"),
                    body_message="Click on the given link to verify your account",
                    route="user/verify-account",
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

        user_data["password"] = password_manager.hash(user_data["password1"])
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
        access_token, access_jti, access_exp = oauth.create_access_token(
            {"sub": str(inserted_id.inserted_id), "ver": user_data.get("passVer")}
        )

        # SEND EMAIL TO THE USER TO VERIFY THE ACCOUNT
        send_email(
            token=access_token,
            subject="Verify Account - HOMESETV",
            recipient_email=user_data.get("email"),
            body_message="Click on the given link to verify your account",
            route="user/verify-account",
        )

        # TODO: Log - I
        return {"detail": "user registered successfully", "status_code": response.status_code}

    except Exception as ex:
        # TODO: Log - C {ex}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"internal server error {ex}",
        )


@router.get(path="/verify-account/", response_class=HTMLResponse)
def check_user_email(request: Request, response: Response):
    token = request.query_params.get("token")
    token_data =oauth.get_current_user(token=token)
    update_result = app.col_user.update_one({"_id": ObjectId(token_data.get("sub"))}, {"$set": {"active": True}})
    if update_result:
        response.status_code = status.HTTP_200_OK
        html_content = get_template(html_file_name="account_verified.html")
        return HTMLResponse(content=html_content)
    html_content = get_template(html_file_name="account_not_verified.html") 
    return HTMLResponse(content=html_content, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
