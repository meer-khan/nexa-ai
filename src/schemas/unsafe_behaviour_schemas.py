from pydantic import BaseModel, validator
from typing import List
from datetime import datetime


ALLOWED_VIOLATIONS = [
    "people off pathways",
    "using mobile while walking",
    "not holding railings",
    "running in walkways",
]


class ViolationRequest(BaseModel):
    camera_id: str
    violations: List[str]

    @validator("violations", each_item=True)
    def validate_violation(cls, v):
        if v not in ALLOWED_VIOLATIONS:
            raise ValueError(f"Violation '{v}' is not allowed.")
        return v
