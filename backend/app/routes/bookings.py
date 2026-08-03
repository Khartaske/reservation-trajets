from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models import Booking, Trip, db

bookings_bp = Blueprint("bookings", __name__, url_prefix="/api/bookings")


@bookings_bp.post("")
@jwt_required()
def create_booking():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Corps JSON manquant ou invalide."}), 400

    trip_id = data.get("trip_id")
    seats = data.get("seats")
    if not isinstance(trip_id, int) or isinstance(trip_id, bool):
        return jsonify({"error": "Le champ trip_id doit être un entier."}), 400
    if not isinstance(seats, int) or isinstance(seats, bool) or seats < 1:
        return (
            jsonify(
                {"error": "Le champ seats doit être un entier supérieur ou égal à 1."}
            ),
            400,
        )

    trip = db.session.execute(
        db.select(Trip).where(Trip.id == trip_id).with_for_update()
    ).scalar_one_or_none()
    if trip is None:
        return jsonify({"error": "Trajet introuvable."}), 404

    remaining = trip.remaining_seats()
    if seats > remaining:
        if remaining <= 0:
            message = "Ce trajet est complet : plus aucune place disponible."
        else:
            message = (
                f"Places insuffisantes : il ne reste que {remaining} "
                f"place(s) disponible(s) sur ce trajet."
            )
        return jsonify({"error": message}), 409

    booking = Booking(
        user_id=int(get_jwt_identity()),
        trip_id=trip.id,
        seats_booked=seats,
        status="confirmed",
    )
    db.session.add(booking)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({"booking": booking.to_dict()}), 201


@bookings_bp.get("")
@jwt_required()
def list_my_bookings():
    user_id = int(get_jwt_identity())
    bookings = (
        db.session.execute(
            db.select(Booking)
            .where(Booking.user_id == user_id)
            .order_by(Booking.created_at.desc(), Booking.id.desc())
        )
        .scalars()
        .all()
    )
    return jsonify({"bookings": [b.to_dict() for b in bookings]}), 200


@bookings_bp.delete("/<int:booking_id>")
@jwt_required()
def cancel_booking(booking_id: int):
    booking = db.session.get(Booking, booking_id)
    if booking is None:
        return jsonify({"error": "Réservation introuvable."}), 404
    if booking.user_id != int(get_jwt_identity()):
        return jsonify({"error": "Cette réservation ne vous appartient pas."}), 403

    booking.status = "cancelled"
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({"message": "Réservation annulée.", "booking": booking.to_dict()}), 200
