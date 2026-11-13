from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ElectionBase(BaseModel):
    election_code: str = Field(max_length=50)
    name: str = Field(max_length=200)
    description: str | None = None
    start_at: datetime
    end_at: datetime
    status: str = "draft"


class ElectionCreate(ElectionBase):
    pass


class ElectionUpdate(BaseModel):
    election_code: str | None = Field(default=None,max_length=50)
    name: str | None = Field(default=None,max_length=200)
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    status: str | None = None


class ElectionResponse(ElectionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ElectionVoterRollBase(BaseModel):
    election_id: int
    voter_id: int
    polling_station_id: int


class ElectionVoterRollCreate(ElectionVoterRollBase):
    pass


class ElectionVoterRollResponse(ElectionVoterRollBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    added_at: datetime