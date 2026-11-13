from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AddressBase(BaseModel):
    door_no: str | None = Field(default=None, max_length=50)
    street: str | None = Field(default=None, max_length=150)
    village_town: str | None = Field(default=None, max_length=150)
    city: str | None = Field(default=None, max_length=100)
    district: str = Field(max_length=100)
    state: str = Field(max_length=100)
    pincode: str | None = Field(default=None, max_length=10)


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    door_no: str | None = Field(default=None, max_length=50)
    street: str | None = Field(default=None, max_length=150)
    village_town: str | None = Field(default=None, max_length=150)
    city: str | None = Field(default=None, max_length=100)
    district: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    pincode: str | None = Field(default=None, max_length=10)


class AddressResponse(AddressBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class PollingStationBase(BaseModel):
    station_code: str = Field(max_length=50)
    name: str = Field(max_length=150)
    address_id: int | None = None
    location_description: str | None = Field(default=None,max_length=255)
    is_active: bool = True


class PollingStationCreate(PollingStationBase):
    pass


class PollingStationUpdate(BaseModel):
    station_code: str | None = Field(default=None, max_length=50)
    name: str | None = Field(default=None, max_length=150)
    address_id: int | None = None
    location_description: str | None = Field(default=None,max_length=255)
    is_active: bool | None = None


class PollingStationResponse(PollingStationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime