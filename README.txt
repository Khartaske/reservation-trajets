Réservation de trajets
======================

Plateforme web de réservation de trajets : un voyageur recherche un trajet
(ville de départ, ville d'arrivée, date), réserve un nombre de places, puis
consulte ou annule ses réservations.

Pile technique
--------------

    Frontend .......... Angular 22 (à venir)
    Backend ........... Python 3.13 · Flask 3.1
    Base de données ... PostgreSQL 18

Avancement
----------

- Schéma de la base finalisé et validé : 3 tables (users, trips,
  bookings) avec contraintes — voir docs/schema-base-de-donnees.txt.
- Modèles SQLAlchemy branchés sur PostgreSQL et script seed.py
  rejouable (~30 trajets réalistes entre villes françaises).
- Premiers endpoints : GET /api/health, GET /api/trips (filtres
  origine / destination / date) et GET /api/trips/<id>.
- À venir : authentification JWT et endpoints de réservation.

Règle métier centrale
---------------------

Les places restantes d'un trajet ne sont jamais stockées : elles sont
recalculées à chaque demande selon la formule
« capacité − somme des places des réservations "confirmed" ». Annuler une
réservation reviendra simplement à passer son statut à « cancelled ».

Installation
------------

Prérequis
~~~~~~~~~

- Git
- Python 3.12 ou plus récent
- PostgreSQL 18

Backend (API Flask)
~~~~~~~~~~~~~~~~~~~

    cd backend

    python -m venv venv
    venv\Scripts\activate        (Windows)
    source venv/bin/activate     (Linux / macOS)

    pip install -r requirements.txt

    copy .env.example .env       (Windows — puis renseigner les valeurs)
    cp .env.example .env         (Linux / macOS)

    flask run --debug --port 5000

Base de données (PostgreSQL 18)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    psql -U postgres -c "CREATE DATABASE reservation_db;"

    cd backend
    venv\Scripts\python.exe seed.py

Le script seed.py est rejouable à volonté : il crée les tables si
nécessaire, vide les données puis réinsère le même jeu (30 trajets, dates
passées et futures, deux comptes de démonstration pour la suite du
projet).

Endpoints disponibles
---------------------

    GET /api/health
        État de santé de l'API
    GET /api/trips
        Trajets futurs triés par départ, filtres
        ?origin=&destination=&date=, places restantes incluses
    GET /api/trips/<id>
        Détail d'un trajet (404 si inconnu)

Vérification rapide :

    curl http://localhost:5000/api/health
    curl "http://localhost:5000/api/trips?origin=Paris&destination=Lyon"
