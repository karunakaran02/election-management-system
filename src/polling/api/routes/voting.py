from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from polling.core.dependencies import get_current_user
from polling.database import get_db
from polling.models.users import User
from polling.models import (
    Voter,
    ElectionVoterRoll,
    VoterParticipation,
    PollingOfficer,
)
from polling.schema.voting import VoteRequest, VoteResponse

router = APIRouter(prefix="/voting", tags=["Voting"])


async def require_polling_officer(current_user: User = Depends(get_current_user)):
    if current_user.role != "polling_officer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Polling officier is required")
    return current_user

@router.get("/polls")
async def get_polls(current_user: User = Depends(get_current_user),db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Voter).where(Voter.user_id == current_user.id))

    voter = result.scalar_one_or_none()

    if voter is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="User is not registered as a voter")

    result = await db.execute(select(ElectionVoterRoll).where(ElectionVoterRoll.voter_id == voter.id))
    rolls = result.scalars().all()

    return {
        "voter_id": voter.id,
        "polls": [
            {
                "election_id": roll.election_id,
                "polling_station_id": roll.polling_station_id,
            }
            for roll in rolls
        ],
    }

@router.post("/{election_id}/vote", response_model=VoteResponse)
async def cast_vote(election_id: int,data: VoteRequest,current_user: User = Depends(get_current_user),db: AsyncSession = Depends(get_db),):
    result = await db.execute(select(PollingOfficer).where(PollingOfficer.user_id == current_user.id))

    officer = result.scalar_one_or_none()

    if officer is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only polling officers can record a vote",)

    result = await db.execute(select(Voter).where(Voter.voter_code == data.voter_code))
    voter = result.scalar_one_or_none()

    if voter is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Voter not found")

    result = await db.execute(select(ElectionVoterRoll).where(ElectionVoterRoll.election_id == election_id,ElectionVoterRoll.voter_id == voter.id,))
    roll = result.scalar_one_or_none()

    if roll is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Voter is not registered for this election")

    result = await db.execute(select(VoterParticipation).where(VoterParticipation.election_voter_roll_id == roll.id))

    existing_participation = result.scalar_one_or_none()

    if existing_participation is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Voter has already voted")

    participation = VoterParticipation(
        election_voter_roll_id=roll.id,
        polling_station_id=roll.polling_station_id,
        polling_officer_id=officer.id,
        status="completed",
    )

    db.add(participation)

    await db.commit()
    await db.refresh(participation)

    return VoteResponse(
        message="Vote recorded successfully",
        election_voter_roll_id=participation.election_voter_roll_id,
        polling_station_id=participation.polling_station_id,
        polled_at=participation.polled_at,
    )
    result = await db.execute(select(Voter).where(Voter.user_id == current_user.id))
    voter = result.scalar_one_or_none()

    if voter is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not registered as a voter",)


    result = await db.execute(select(ElectionVoterRoll).where(ElectionVoterRoll.election_id == election_id,ElectionVoterRoll.voter_id == voter.id))
    roll = result.scalar_one_or_none()

    if roll is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Voter is not registered for this election")

    result = await db.execute(select(VoterParticipation).where(VoterParticipation.election_voter_roll_id == roll.id))
    participation = result.scalar_one_or_none()

    if participation is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Voter has already voted")

    result = await db.execute(select(PollingOfficer).where(PollingOfficer.user_id == current_user.id))
    officer = result.scalar_one_or_none()

    if officer is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only polling officers can record a vote")

    participation = VoterParticipation(
    election_voter_roll_id=roll.id,
    polling_station_id=roll.polling_station_id,
    polling_officer_id=officer.id,
    status="completed",
    )

    db.add(participation)
    await db.commit()
    await db.refresh(participation)

    return VoteResponse(
    message="Vote recorded successfully",
    election_voter_roll_id=participation.election_voter_roll_id,
    polling_station_id=participation.polling_station_id,
    polled_at=participation.polled_at,
    )
