from fastapi import status, APIRouter, Response, HTTPException, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from typing_extensions import Dict, Any
from db import db_query
from bson import ObjectId
import datetime
from utils import jwt_helper, hash_helper
from icecream import ic
import app

router = APIRouter(tags=["user-management"], prefix="/user")


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    response: Response, user_credentials: OAuth2PasswordRequestForm = Depends()
):
    try:
        query_obj = db_query.Queries()
        user: dict = app.col_user.find_one({"email": user_credentials.username, "active": True})
        # check if user does not exists
        if not user:
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
            )

        else:
            # user exists
            result: bool = hash_helper.verify(
                user_credentials.password, user.get("password")
            )
            # incorrect password
            if not result:
                response.status_code = status.HTTP_401_UNAUTHORIZED
                return HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found"
                )
            else:
                # creation of access token
                access_token, access_jti, access_exp = jwt_helper.create_access_token(
                    {"sub": str(user.get("_id")), "ver": user.get("passVer")}
                )

                # creation of refresh token
                refresh_token, refresh_jti, refresh_exp = jwt_helper.create_refresh_token(
                    {"sub": str(user.get("_id")), "ver": user.get("passVer")}
                )

                # delete old tokens for specific user
                query_dict = query_obj.get_delete_token_query_dict(
                    user_id=str(user.get("_id"))
                )
                app.col_user.delete_one(query_dict)
                # db_query.delete_record(
                #     collection=app.col_valid_tokens, data_dict=query_dict
                # )
                if user.get("plan"):
                    plan_time_left = user.get("planEndAt").replace(
                        tzinfo=datetime.timezone.utc
                    ) - datetime.datetime.now(datetime.UTC)
                    plan_time_left = plan_time_left.days
                else:
                    plan_time_left = None
                if plan_time_left == 0:
                    set_plan_null()
                ic(user.get("plan"))
                plan_id =user.get("plan")
                plan = app.col_user.find_one(filter={"plan": user.get("plan")})
                ic(plan)
                plan = app.col_plan.find_one(filter={"_id": ObjectId(plan_id)})
                ic(plan)
                # plan = db_query.find_single_record(
                #     collection=app.col_plan, data_dict=user.get("plan")
                # )
                # insert valid token for a user
                query_dict = query_obj.get_insert_token_query_dict(
                    access_uuid=access_jti,
                    refresh_uuid=refresh_jti,
                    exp_access=access_exp,
                    exp_refresh=refresh_exp,
                    user_id=str(user.get("_id")),
                )
                app.col_valid_tokens.insert_one(document=query_dict)
                # db_query.insert_records(
                #     collection=app.col_valid_tokens, data_dict=query_dict
                # )

                return {
                    "accessToken": access_token,
                    "refreshToken": refresh_token,
                    "tokenType": "bearer",
                    "roles": user.get("roles"),
                    "planType": plan.get("name"),
                    "planDaysLeft": plan_time_left,
                    "status_code": response.status_code
                }

    except Exception as ex:
        # TODO: LOG - C {ex}
        ic(ex)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="internal server error",
        )


def set_plan_null(user_id: str):
    filter_query = {"_id": ObjectId(user_id)}
    update_query = {"$set": {"plan": None}}
    app.col_user.update_one(filter=filter_query, update=update_query)
    # db_query.update_single_record(
    #     collection=app.col_user, filter_dict=filter_query, update_dict=update_query
    # )
