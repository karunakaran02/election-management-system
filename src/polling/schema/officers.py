from pydantic import BaseModel, ConfigDict
from datetime import datetime


class OfficerCreateRequest(BaseModel):
    name: str
    username: str
    password: str
    employee_code: str


class OfficerResponse(BaseModel):
    id: int
    user_id: int
    name: str
    username: str
    employee_code: str
    role: str
    created_at: datetime


class OfficerPutRequest(BaseModel):
    name: str
    username: str
    employee_code: str


class OfficerPatchRequest(BaseModel):
    name: str | None = None
    username: str | None = None
    employee_code: str | None = None

    model_config = ConfigDict(extra="forbid")