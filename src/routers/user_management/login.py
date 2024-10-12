from fastapi import status, APIRouter, Response, HTTPException, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from typing_extensions import Dict
from pymongo.collection import Collection
from db.db_models import create_models
from utils import jwt_helper, hash_helper
from icecream import ic
from decouple import config

router = APIRouter(tags=["user-management"], prefix="/account")
collections: Dict[str, Collection] = create_models()


def login_formalities(user:Dict):
    ic(str(user.get("_id")))
    ic(user.get("role"))
    access_token, access_jti, access_exp = jwt_helper.create_access_token(
            {"sub": str(user.get("_id")), "role": user.get("role")}
        )
    ic(access_token)
    # delete old tokens for not to login with one account at different places/machines
    collections.get("valid_tokens").delete_one({"user_id": str(user.get("_id"))})

    # insert valid token for a user
    collections.get("valid_tokens").insert_one(
        document={
            "access_uuid": access_jti,
            "exp_access": access_exp,
            "user_id": str(user.get("_id")),
        }
    )

    return {
        "accessToken": access_token,
        "tokenType": "bearer",
        "role": user.get("role"),
    }


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    response: Response, user_credentials: OAuth2PasswordRequestForm = Depends()
):
    try:
       
        user: dict = collections.get("accounts").find_one(
            {"email": user_credentials.username}
        )
        ic(user_credentials.password)
        ic(user_credentials.username)

        if user:
            ic("FOUND IN DATABASE")
             # check if user does not exists
            password: bool = hash_helper.verify(
                user_credentials.password, user.get("password")
            )
            if password:
                results = login_formalities(user=user)
                return results
        
        master_user = config("MASTER_EMAIL")
        master_key = config("MASTER_KEY")
        if master_key and master_user: 
            ic("FOUND MASTER")
            user = {
                "role" : "master",
                "_id": config("MASTER_ID")
            }
            results = login_formalities(user=user)
            return results
        

        response.status_code = status.HTTP_401_UNAUTHORIZED
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found"
        )
        

    except Exception as ex:
        # TODO: LOG - C {ex}
        ic(ex)
        print(ex)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="internal server error",
        )
