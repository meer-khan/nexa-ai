from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security.oauth2 import OAuth2PasswordBearer
from typing_extensions import Dict, Tuple
from fastapi import Depends, HTTPException, status
from decouple import config
import uuid

oauth_scheme = OAuth2PasswordBearer(tokenUrl="login")


SECRET_KEY_ACCESS = config("SECRET_KEY_ACCESS")
SECRET_KEY_REFRESH = config("SECRET_KEY_REFRESH")
ALGORITHM = config("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 10
REFRESH_TOKEN_EXPIRE_DAYS = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 10
ISS = "www.homesetv.com"


def create_access_token(data: dict) -> Tuple:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    jti = str(uuid.uuid4())
    to_encode.update({"iss": ISS, "exp": expire, "jti": jti})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY_ACCESS, algorithm=ALGORITHM)
    return encoded_jwt, jti, expire


def verify_token(token: str, credentials_exception) -> Dict:
    try:
        payload = jwt.decode(token, SECRET_KEY_ACCESS, algorithms=ALGORITHM)

        if (
            payload.get("iss") != ISS
            or payload.get("sub") is None
            or payload.get("ver") is None
        ):
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception


def create_refresh_token(data: dict) -> Dict:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    jti = str(uuid.uuid4())
    to_encode.update({"iss": ISS, "exp": expire, "jti": jti})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY_REFRESH, algorithm=ALGORITHM)
    return encoded_jwt, jti, expire


def verify_refresh_token(token: str, credentials_exception) -> Dict:
    try:
        payload = jwt.decode(token, SECRET_KEY_REFRESH, algorithms=ALGORITHM)

        if (
            payload.get("iss") != ISS
            or payload.get("sub") is None
            or payload.get("ver") is None
        ):
            raise credentials_exception

        return payload

    except JWTError:
        raise credentials_exception


def get_refresh_token(token: str = Depends(oauth_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized user",
        headers={"WWW.Authenticate": "Bearer"},
    )

    return verify_refresh_token(token, credentials_exception)


def get_current_user(token: str = Depends(oauth_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="unauthorized user",
        headers={"WWW.Authenticate": "Bearer"},
    )

    return verify_token(token, credentials_exception)


