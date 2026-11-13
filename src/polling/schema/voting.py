from datetime import datetime
from pydantic import BaseModel


class VoteRequest(BaseModel):
    voter_code: str


class VoteResponse(BaseModel):
    message: str
    election_voter_roll_id: int
    polling_station_id: int
    polled_at: datetime