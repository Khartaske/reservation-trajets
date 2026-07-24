from datetime import datetime
from decimal import Decimal
from typing import Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    bookings: Mapped[list["Booking"]] = relationship(back_populates="user")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Trip(db.Model):
    __tablename__ = "trips"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_trips_price_positive"),
        CheckConstraint("capacity > 0", name="ck_trips_capacity_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    origin: Mapped[str] = mapped_column(String(100))
    destination: Mapped[str] = mapped_column(String(100))
    departure_at: Mapped[datetime] = mapped_column(DateTime)
    arrival_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    price: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    capacity: Mapped[int] = mapped_column()

    bookings: Mapped[list["Booking"]] = relationship(back_populates="trip")

    @classmethod
    def remaining_seats_for(cls, trips: list["Trip"]) -> dict[int, int]:
        if not trips:
            return {}
        rows = db.session.execute(
            db.select(Booking.trip_id, func.sum(Booking.seats_booked))
            .where(
                Booking.trip_id.in_([t.id for t in trips]),
                Booking.status == "confirmed",
            )
            .group_by(Booking.trip_id)
        ).all()
        booked = dict(rows)
        return {t.id: t.capacity - int(booked.get(t.id, 0)) for t in trips}

    def remaining_seats(self) -> int:
        return Trip.remaining_seats_for([self])[self.id]

    def to_dict(self, remaining_seats: int | None = None) -> dict:
        if remaining_seats is None:
            remaining_seats = self.remaining_seats()
        return {
            "id": self.id,
            "origin": self.origin,
            "destination": self.destination,
            "departure_at": self.departure_at.isoformat(),
            "arrival_at": self.arrival_at.isoformat() if self.arrival_at else None,
            "price": float(self.price),
            "capacity": self.capacity,
            "remaining_seats": remaining_seats,
        }


class Booking(db.Model):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint("seats_booked >= 1", name="ck_bookings_seats_min"),
        CheckConstraint(
            "status IN ('confirmed', 'cancelled')", name="ck_bookings_status"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"))
    seats_booked: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column(String(20), default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="bookings")
    trip: Mapped["Trip"] = relationship(back_populates="bookings")

    def to_dict(self, include_trip: bool = True) -> dict:
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "trip_id": self.trip_id,
            "seats_booked": self.seats_booked,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_trip:
            data["trip"] = self.trip.to_dict()
        return data
