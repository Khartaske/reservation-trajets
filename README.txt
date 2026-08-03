Réservation de trajets
======================

Plateforme web de réservation de trajets : un voyageur recherche un trajet
(ville de départ, ville d'arrivée, date), réserve un nombre de places, puis
consulte ou annule ses réservations.

Pile technique
--------------

    Frontend .......... Angular 22 (composants standalone, CSS artisanal)
    Backend ........... Python 3.13 · Flask 3.1
    Base de données ... PostgreSQL 18

Avancement
----------

- API REST complète : les 9 endpoints (santé, authentification JWT,
  trajets, réservations) avec gestion d'erreurs cohérente en français.
- Scénario de recette rejouable, en collection Thunder Client
  (docs/collection-thunder-client.json) et en script équivalent
  (docs/scenario-api.ps1) : inscription -> connexion -> recherche ->
  réservation -> sur-réservation refusée (409) -> annulation -> places
  redevenues disponibles.
- Tranche verticale : une première page Angular affiche les trajets
  réels de PostgreSQL à travers l'API Flask (proxy /api en place).
- À venir : les écrans complets de l'application (recherche, résultats,
  détail, connexion, mes réservations).

Installation
------------

Prérequis
~~~~~~~~~

- Git
- Node.js 24 LTS (avec npm)
- Angular CLI 22 : npm install -g @angular/cli
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

Le script seed.py est rejouable à volonté (30 trajets entre villes
françaises, deux comptes de démonstration — mot de passe
motdepasse123 : sophie.martin@example.fr, lucas.bernard@example.fr).

Règle métier centrale : les places restantes d'un trajet ne sont jamais
stockées ; elles sont recalculées à chaque demande selon la formule
« capacité − somme des places des réservations "confirmed" »
(voir docs/schema-base-de-donnees.txt).

Frontend (tranche verticale)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    cd frontend

    npm install

    ng serve --port 4200

La page servie sur http://localhost:4200 affiche les prochains départs
réels de la base, à travers le proxy /api -> Flask (port 5000).

API REST
--------

Toutes les réponses sont en JSON. En cas d'erreur, le corps est toujours
{"error": "message en français"} avec le code HTTP approprié :
400 (champ manquant ou invalide), 401 (identifiants ou jeton invalides),
403 (ressource d'un autre voyageur), 404 (introuvable), 409 (conflit
métier : email déjà pris, places insuffisantes).

    GET /api/health                                          Auth : aucune
        État de santé de l'API
    POST /api/auth/register                                  Auth : aucune
        Inscription (409 si email déjà utilisé, mot de passe haché)
    POST /api/auth/login                                     Auth : aucune
        Connexion : renvoie un jeton JWT (24 h) et le profil
    GET /api/auth/me                                         Auth : JWT
        Profil du voyageur identifié par le jeton
    GET /api/trips                                           Auth : aucune
        Trajets futurs triés par départ, filtres
        ?origin=&destination=&date=, places restantes incluses
    GET /api/trips/<id>                                      Auth : aucune
        Détail d'un trajet (404 si inconnu)
    POST /api/bookings                                       Auth : JWT
        Réserver {trip_id, seats} — recalcul côté serveur, 409 si places
        insuffisantes
    GET /api/bookings                                        Auth : JWT
        Les réservations du voyageur courant, avec les infos du trajet
    DELETE /api/bookings/<id>                                Auth : JWT
        Annuler (statut -> cancelled), 403 si autre voyageur, 404 si
        inconnue

Corps des requêtes et des réponses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    POST /api/auth/register   -> { "email", "password", "full_name" }
      201 -> { "user": { id, email, full_name, created_at } }

    POST /api/auth/login      -> { "email", "password" }
      200 -> { "token": "…jwt…", "user": { … } }

    GET  /api/auth/me         (en-tête Authorization: Bearer <jeton>)
      200 -> { "user": { … } }

    GET  /api/trips[?origin=&destination=&date=AAAA-MM-JJ]
      200 -> { "trips": [ { id, origin, destination, departure_at, arrival_at,
                            price, capacity, remaining_seats } ] }

    GET  /api/trips/<id>
      200 -> { "trip": { … } }

    POST /api/bookings        -> { "trip_id": 18, "seats": 2 }   (JWT)
      201 -> { "booking": { id, user_id, trip_id, seats_booked, status,
                            created_at, trip: { … } } }

    GET  /api/bookings        (JWT)
      200 -> { "bookings": [ { …, trip: { … } } ] }

    DELETE /api/bookings/<id> (JWT)
      200 -> { "message": "Réservation annulée.", "booking": { … } }

Les dates sont échangées au format ISO (heure locale naïve).

Scénario de recette — deux formats
----------------------------------

Le même parcours (inscription -> connexion -> recherche -> réservation ->
sur-réservation refusée -> annulation -> places libérées) est fourni sous
deux formes complémentaires :

    docs/collection-thunder-client.json
        Collection Thunder Client (le format demandé par la feuille de
        route). À importer dans l'extension Thunder Client de VS Code,
        avec docs/environnement-thunder-client.json. Le jeton JWT obtenu
        à la connexion est capturé dans une variable d'environnement et
        réutilisé automatiquement par les requêtes protégées : le
        scénario se rejoue sans copier-coller.

    docs/scenario-api.ps1
        Équivalent scriptable du même scénario, exécuté en une seule
        commande. C'est la forme utilisée pour la vérification
        automatisée (chaque étape affiche la requête, le code HTTP et la
        réponse) :

    powershell -ExecutionPolicy Bypass -File docs\scenario-api.ps1

Prérequis dans les deux cas : l'API démarrée sur le port 5000 et la base
fraîchement peuplée (python seed.py), afin que l'inscription renvoie 201
et que le trajet 18 soit bien un trajet futur.
