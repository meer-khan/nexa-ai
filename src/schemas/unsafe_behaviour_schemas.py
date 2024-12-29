from pydantic import BaseModel, field_validator
from typing import List
from datetime import datetime
from icecream import ic

ALLOWED_VIOLATIONS = [
    "people off pathways",
    "using mobile while walking",
    "not holding railings",
    "running in walkways",
]


class ViolationRequest(BaseModel):
    cameraId: str
    violations: List[str]

    @field_validator("violations", mode="after")
    def validate_violation(cls, v):
        for violation in v:
            if violation not in ALLOWED_VIOLATIONS:
                raise ValueError(
                    f"Violation '{v}' is not allowed. Only following violations are allowed {ALLOWED_VIOLATIONS}"
                )
            return v
