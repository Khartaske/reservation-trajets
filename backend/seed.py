import random
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import text
from werkzeug.security import generate_password_hash

from app import create_app
from app.models import Booking, Trip, User, db

random.seed(42)

ROUTES = [
    ("Paris", "Lyon", 115, Decimal("45.00")),
    ("Lyon", "Paris", 115, Decimal("45.00")),
    ("Paris", "Marseille", 200, Decimal("69.00")),
    ("Marseille", "Paris", 200, Decimal("69.00")),
    ("Paris", "Bordeaux", 130, Decimal("59.00")),
    ("Bordeaux", "Paris", 130, Decimal("59.00")),
    ("Paris", "Lille", 65, Decimal("39.00")),
    ("Lille", "Paris", 65, Decimal("39.00")),
    ("Paris", "Strasbourg", 110, Decimal("55.00")),
    ("Strasbourg", "Paris", 110, Decimal("55.00")),
    ("Lyon", "Marseille", 105, Decimal("35.00")),
    ("Marseille", "Lyon", 105, Decimal("35.00")),
    ("Marseille", "Nice", 150, Decimal("29.00")),
    ("Nice", "Marseille", 150, Decimal("29.00")),
    ("Toulouse", "Bordeaux", 135, Decimal("25.00")),
    ("Bordeaux", "Toulouse", 135, Decimal("25.00")),
    ("Nantes", "Paris", 120, Decimal("49.00")),
    ("Paris", "Nantes", 120, Decimal("49.00")),
    ("Rennes", "Paris", 90, Decimal("45.00")),
    ("Paris", "Rennes", 90, Decimal("45.00")),
    ("Montpellier", "Lyon", 115, Decimal("39.00")),
    ("Lyon", "Montpellier", 115, Decimal("39.00")),
    ("Lille", "Lyon", 180, Decimal("59.00")),
    ("Strasbourg", "Lyon", 220, Decimal("49.00")),
    ("Grenoble", "Lyon", 85, Decimal("19.00")),
    ("Lyon", "Grenoble", 85, Decimal("19.00")),
    ("Dijon", "Paris", 100, Decimal("42.00")),
    ("Paris", "Dijon", 100, Decimal("42.00")),
    ("Marseille", "Montpellier", 105, Decimal("25.00")),
    ("Angers", "Paris", 95, Decimal("39.00")),
]


def build_trips() -> list[Trip]:
    trips = []
    now = datetime.now().replace(second=0, microsecond=0)
    for origin, destination, duration_min, base_price in ROUTES:
        offset_days = random.randint(-20, 45)
        departure = (now + timedelta(days=offset_days)).replace(
            hour=random.randint(6, 20), minute=random.choice([0, 15, 30, 45])
        )
        arrival = departure + timedelta(minutes=duration_min)
        variation = Decimal(str(round(random.uniform(0.85, 1.15), 2)))
        price = (base_price * variation).quantize(Decimal("0.01"))
        capacity = random.choice([30, 35, 40, 45, 50, 55, 60])
        trips.append(
            Trip(
                origin=origin,
                destination=destination,
                departure_at=departure,
                arrival_at=arrival,
                price=price,
                capacity=capacity,
            )
        )
    return trips


def main() -> None:
    app = create_app()
    with app.app_context():
        db.create_all()

        db.session.execute(
            text("TRUNCATE TABLE bookings, trips, users RESTART IDENTITY CASCADE")
        )
        print("Base vidée (TRUNCATE), identifiants réinitialisés.")

        trips = build_trips()
        db.session.add_all(trips)

        demo_password = "motdepasse123"
        sophie = User(
            email="sophie.martin@example.fr",
            password_hash=generate_password_hash(demo_password),
            full_name="Sophie Martin",
        )
        lucas = User(
            email="lucas.bernard@example.fr",
            password_hash=generate_password_hash(demo_password),
            full_name="Lucas Bernard",
        )
        db.session.add_all([sophie, lucas])

        bookings = [
            Booking(user=sophie, trip=trips[0], seats_booked=3, status="confirmed"),
            Booking(user=lucas, trip=trips[0], seats_booked=2, status="confirmed"),
            Booking(user=sophie, trip=trips[0], seats_booked=4, status="cancelled"),
            Booking(user=lucas, trip=trips[1], seats_booked=1, status="confirmed"),
            Booking(user=sophie, trip=trips[2], seats_booked=5, status="cancelled"),
            Booking(user=lucas, trip=trips[3], seats_booked=2, status="confirmed"),
        ]
        db.session.add_all(bookings)

        db.session.commit()

        print(f"{len(trips)} trajets insérés entre villes françaises.")
        print(
            f"2 voyageurs de démonstration insérés "
            f"(mot de passe commun : {demo_password})."
        )
        print(f"{len(bookings)} réservations de démonstration insérées.")
        print("Peuplement terminé avec succès.")


if __name__ == "__main__":
    main()
