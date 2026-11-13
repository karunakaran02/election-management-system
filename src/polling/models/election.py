from __future__ import annotations
from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from polling.database import Base
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)

if TYPE_CHECKING:
    from polling.models.address import PollingStation
    from polling.models.users import Voter, VoterParticipation

class ElectionStatus(str, PyEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    
class Election(Base):
    __tablename__ = "elections"

    __table_args__ = (
        CheckConstraint(
            "status IN "
            "('draft', 'scheduled', 'active', 'completed', 'cancelled')",
            name="valid_election_status",
        ),
        CheckConstraint(
            "end_at > start_at",
            name="valid_election_period",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    election_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    voter_roll_entries: Mapped[list[ElectionVoterRoll]] = relationship(back_populates="election")


class ElectionVoterRoll(Base):
    __tablename__ = "election_voter_roll"

    __table_args__ = (
        UniqueConstraint(
            "election_id",
            "voter_id",
            name="unique_voter_per_election",
        ),
        UniqueConstraint(
            "id",
            "polling_station_id",
            name="unique_roll_station",
        ),
        Index(
            "idx_election_roll_station",
            "election_id",
            "polling_station_id",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    election_id: Mapped[int] = mapped_column(BigInteger,ForeignKey("elections.id", ondelete="RESTRICT"),nullable=False)
    voter_id: Mapped[int] = mapped_column(BigInteger,ForeignKey("voters.id", ondelete="RESTRICT"),nullable=False)
    polling_station_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("polling_stations.id", ondelete="RESTRICT"),nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    election: Mapped[Election] = relationship(back_populates="voter_roll_entries")
    voter: Mapped[Voter] = relationship(back_populates="election_roll_entries")
    polling_station: Mapped[PollingStation] = relationship(back_populates="election_roll_entries")
    participation: Mapped[VoterParticipation | None] = relationship(back_populates="election_voter_roll",uselist=False)
