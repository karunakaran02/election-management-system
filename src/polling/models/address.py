from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from polling.database import Base
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
    func,
)

if TYPE_CHECKING:
    from polling.models.election import ElectionVoterRoll
    from polling.models.users import Voter


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    door_no: Mapped[str | None] = mapped_column(String(50))
    street: Mapped[str | None] = mapped_column(String(150))
    village_town: Mapped[str | None] = mapped_column(String(150))
    city: Mapped[str | None] = mapped_column(String(100))
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    pincode: Mapped[str | None] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    voters: Mapped[list[Voter]] = relationship(back_populates="address")
    polling_stations: Mapped[list[PollingStation]] = relationship(back_populates="address")


class PollingStation(Base):
    __tablename__ = "polling_stations"

    __table_args__ = (Index("idx_stations_address_id", "address_id"),)

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    station_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    address_id: Mapped[int | None] = mapped_column(BigInteger,ForeignKey("addresses.id", ondelete="RESTRICT"),nullable=True)
    location_description: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    address: Mapped[Address | None] = relationship(back_populates="polling_stations")
    election_roll_entries: Mapped[list[ElectionVoterRoll]] = relationship(back_populates="polling_station")
