from datetime import date, datetime, timedelta

from flask import Blueprint, jsonify, request

from app.models import Trip, db

trips_bp = Blueprint("trips", __name__, url_prefix="/api/trips")


@trips_bp.get("")
def list_trips():
    query = db.select(Trip).where(Trip.departure_at >= datetime.now())

    origin = (request.args.get("origin") or "").strip()
    destination = (request.args.get("destination") or "").strip()
    date_param = (request.args.get("date") or "").strip()

    if origin:
        query = query.where(Trip.origin.ilike(f"%{origin}%"))
    if destination:
        query = query.where(Trip.destination.ilike(f"%{destination}%"))
    if date_param:
        try:
            day = date.fromisoformat(date_param)
        except ValueError:
            return (
                jsonify({"error": "Le paramètre date doit être au format AAAA-MM-JJ."}),
                400,
            )
        start = datetime.combine(day, datetime.min.time())
        query = query.where(
            Trip.departure_at >= start,
            Trip.departure_at < start + timedelta(days=1),
        )

    trips = db.session.execute(query.order_by(Trip.departure_at)).scalars().all()

    remaining = Trip.remaining_seats_for(trips)
    return (
        jsonify({"trips": [t.to_dict(remaining_seats=remaining[t.id]) for t in trips]}),
        200,
    )


@trips_bp.get("/<int:trip_id>")
def get_trip(trip_id: int):
    trip = db.session.get(Trip, trip_id)
    if trip is None:
        return jsonify({"error": "Trajet introuvable."}), 404
    return jsonify({"trip": trip.to_dict()}), 200
