from __future__ import annotations
from datetime import date, datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from polling.database import Base
from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Identity,
    Index,
    String,
    func,
)

if TYPE_CHECKING:
    from polling.models.address import Address, PollingStation
    from polling.models.election import ElectionVoterRoll


class UserRole(str, PyEnum):
    ADMIN = "admin"
    VOTER = "voter"
    POLLING_OFFICER = "polling_officer"


class ElectionStatus(str, PyEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ParticipationStatus(str, PyEnum):
    COMPLETED = "completed"
    VOIDED = "voided"


class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'voter', 'polling_officer')",
            name="valid_user_role",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    proof_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False,server_default=func.now())
    voter: Mapped[Voter | None] = relationship(back_populates="user",uselist=False)
    polling_officer: Mapped[PollingOfficer | None] = relationship(back_populates="user",uselist=False)


class Voter(Base):
    __tablename__ = "voters"

    __table_args__ = (
        Index("idx_voters_address_id", "address_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger,ForeignKey("users.id", ondelete="RESTRICT"),nullable=False,unique=True)
    address_id: Mapped[int | None] = mapped_column(BigInteger,ForeignKey("addresses.id", ondelete="SET NULL"),nullable=True)
    voter_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    user: Mapped[User] = relationship(back_populates="voter")
    address: Mapped[Address | None] = relationship(back_populates="voters")
    election_roll_entries: Mapped[list[ElectionVoterRoll]] = relationship(back_populates="voter")


class PollingOfficer(Base):
    __tablename__ = "polling_officers"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger,ForeignKey("users.id", ondelete="RESTRICT"),nullable=False,unique=True)
    employee_code: Mapped[str | None] = mapped_column(String(50), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    user: Mapped[User] = relationship(back_populates="polling_officer")
    participation_records: Mapped[list[VoterParticipation]] = relationship(back_populates="polling_officer")


class VoterParticipation(Base):
    __tablename__ = "voter_participation"

    __table_args__ = (
        CheckConstraint(
            "status IN ('completed', 'voided')",
            name="valid_participation_status",
        ),
        ForeignKeyConstraint(
            ["election_voter_roll_id", "polling_station_id"],
            [
                "election_voter_roll.id",
                "election_voter_roll.polling_station_id",
            ],
            name="participation_roll_station_fk",
            ondelete="RESTRICT",
        ),
        Index(
            "idx_participation_officer",
            "polling_officer_id",
        ),
        Index(
            "idx_participation_polled_at",
            "polled_at",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    election_voter_roll_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    polling_station_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    polling_officer_id: Mapped[int] = mapped_column(BigInteger,ForeignKey("polling_officers.id", ondelete="RESTRICT"),nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="completed")
    polled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    election_voter_roll: Mapped[ElectionVoterRoll] = relationship(back_populates="participation")
    polling_officer: Mapped[PollingOfficer] = relationship(back_populates="participation_records")
