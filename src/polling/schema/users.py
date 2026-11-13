from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field

class UserBase(BaseModel):
    name: str = Field(max_length=150)
    username: str = Field(max_length=100)
    role: str = Field(max_length=30)
    proof_reference: str | None = Field(default=None,max_length=255)
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=150)
    username: str | None = Field(default=None, max_length=100)
    role: str | None = Field(default=None, max_length=30)
    proof_reference: str | None = Field(default=None,max_length=255)
    is_active: bool | None = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class VoterBase(BaseModel):
    user_id: int
    address_id: int | None = None
    voter_code: str = Field(max_length=50)
    date_of_birth: date | None = None
    is_active: bool = True


class VoterCreate(VoterBase):
    pass


class VoterUpdate(BaseModel):
    address_id: int | None = None
    voter_code: str | None = Field(default=None,max_length=50)
    date_of_birth: date | None = None
    is_active: bool | None = None


class VoterResponse(VoterBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class PollingOfficerBase(BaseModel):
    user_id: int
    employee_code: str | None = Field(default=None,max_length=50)


class PollingOfficerCreate(PollingOfficerBase):
    pass


class PollingOfficerUpdate(BaseModel):
    employee_code: str | None = Field(default=None,max_length=50)


class PollingOfficerResponse(PollingOfficerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class VoterParticipationBase(BaseModel):
    election_voter_roll_id: int
    polling_station_id: int
    polling_officer_id: int
    status: str = "completed"


class VoterParticipationCreate(VoterParticipationBase):
    pass


class VoterParticipationUpdate(BaseModel):
    status: str | None = None


class VoterParticipationResponse(VoterParticipationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    polled_at: datetime
    created_at: datetime