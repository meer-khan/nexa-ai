from pydantic import (
    BaseModel,
    EmailStr,
    ConfigDict,
    StringConstraints,
    field_validator,
    model_validator,
)
import datetime
from typing_extensions import Literal, Annotated


class ActivityDetected(BaseModel):
    intrustionClass: str
    cameraId: str


class PersonIdentification(BaseModel):
    personId: str
    personName: str
    location: str


class AddCamera(BaseModel):
    cameraId: str
    location: str
    cameraType: Literal["entry", "exit", "assembly_line"]


class LogEvent(BaseModel):
    cameraId: str
    name: str | None
    type: Literal["known", "unknown"]
    employeeID: str


# Pydantic model for the request body
class CountPeople(BaseModel):
    start_time: datetime.datetime  # No timezone info; expected to be in PST
    end_time: datetime.datetime  # No timezone info; expected to be in PST


# Model for employee registration data
class Employee(BaseModel):
    name: str
    employeeID: str


class Login(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(strip_whitespace=False, min_length=8)]


class Signup(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    companyName: Annotated[
        str, StringConstraints(strip_whitespace=False, max_length=100, min_length=2)
    ]
    email: EmailStr
    password1: Annotated[str, StringConstraints(strip_whitespace=False, min_length=8)]
    password2: Annotated[str, StringConstraints(strip_whitespace=False, min_length=8)]
    termsConditions: bool

    @field_validator("termsConditions", mode="before")
    @classmethod
    def check_termsConditions(cls, v: bool):
        if v is not True:
            raise ValueError("terms and conditions should be acknowledged")
        return v

    @model_validator(mode="after")
    def check_passwords_match(self):
        pw1 = self.password1
        pw2 = self.password2
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError("passwords do not match")
        return self
