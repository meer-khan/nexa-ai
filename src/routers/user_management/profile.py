from fastapi import (
    status,
    APIRouter,
    Response,
    HTTPException,
    Form,
    Depends,
)
from icecream import ic
from typing_extensions import Dict
from src.schemas import data_schemas
from pymongo.collection import Collection
from db.db_models import create_models
from utils.jwt_helper import get_current_user
from constants.constants import roles
from utils import general_utilities, passwords_helper
from bson import ObjectId
from icecream import ic
# from logging import Logger
router = APIRouter(tags=["user-management"], prefix="/account")
collections: Dict[str, Collection] = create_models()

@router.get("/profile", status_code=status.HTTP_200_OK)
async def view_profile(response:Response, token: str = Depends(get_current_user)):
    """
    Fetch and return the details of the logged-in user.
    """
    try:
        # Verify if the token is valid and corresponds to a user
        # ic(token)
        user = collections.get("accounts").find_one({"_id": ObjectId(token.get("sub"))})
        if not user:
            response.status_code = status.HTTP_404_NOT_FOUND
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        
        if token.get("role") not in roles.values():
            response.status_code = status.HTTP_404_NOT_FOUND
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You donot have necessary permissions")
        
        company_logo_binary = user.get("companyLogo") 

        if company_logo_binary:
            company_logo_base64 = general_utilities.binary_into_utf8(img=company_logo_binary)

        else:
            company_logo_base64 = None

        return {
            "companyName": user.get("companyName"),
            "email": user.get("email"),
            "role": user.get("role"),
            "companyLogo": company_logo_base64,  # Optional
        }

    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {ex}",
        )




@router.put("/profile/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    response: Response,
    oldPassword: str = Form(...),
    newPassword: str = Form(...),
    token: str = Depends(get_current_user)
):
    """
    Allow users to change their password by verifying the old one first.
    """
    try:
        # Find the user by token
        user = collections.get("accounts").find_one({"_id": ObjectId(token.get("sub"))})

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        
        # verify role (does not apply on master role because master user doesnot exists in database)
        if token.get("role") not in roles.values():
            response.status_code = status.HTTP_404_NOT_FOUND
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You donot have necessary permissions")
        
        # Validate password
        try: 
            data_schemas.ChangePassword(newPassword=newPassword, oldPassword=oldPassword)
        except Exception as ex: 
            response.status_code = status.HTTP_400_BAD_REQUEST
            return HTTPException(status_code=response.status_code, detail=f"Error: {ex}")

        # Verify old password
        if not passwords_helper.verify(oldPassword, user.get("password")):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return HTTPException(
                status_code=response.status_code ,
                detail="Old password is incorrect."
            )

        # Hash new password
        hashed_password = passwords_helper.hash(newPassword)

        # Update the password in the database
        collections.get("accounts").update_one(
            {"_id": ObjectId(token.get("sub"))}, {"$set": {"password": hashed_password}}
        )

        collections.get("valid_tokens").delete_one({"user_email": str(user.get("email"))})

        return {"detail": "Password updated successfully"}

    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {ex}",
        )



#  TODO: TESTING  REQUIRED
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(token: str = Depends(get_current_user)):
    """
    Logs out the user by removing the valid token from the database.
    """
    try:
        # Find the user in the valid tokens collection by the token UUID
        token_record = collections.get("valid_tokens").find_one({"access_uuid": token.get("jti")})

        if not token_record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found or already invalid.")

        # Delete the token to log out the user
        collections.get("valid_tokens").delete_one({"access_uuid": token.get("jti")})

        return {"detail": "Successfully logged out."}

    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {ex}"
        )
