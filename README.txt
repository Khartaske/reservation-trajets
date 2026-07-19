Réservation de trajets
======================

Plateforme web de réservation de trajets : un voyageur recherche un trajet
(ville de départ, ville d'arrivée, date), réserve un nombre de places, puis
consulte ou annule ses réservations. Un seul rôle : voyageur.

Pile technique retenue
----------------------

    Frontend .......... Angular 22
    Backend ........... Python 3.12+ · Flask 3.1
    Base de données ... PostgreSQL 18

Contenu de cette semaine — analyse des besoins
----------------------------------------------

Cette première semaine couvre la phase d'analyse : étude de l'existant,
cahier des charges et maquettes.

    docs/analyse/etude-existant.txt
        Grille comparative de trois plateformes de réservation
        (BlaBlaCar, SNCF Connect, FlixBus) et enseignements retenus
    docs/analyse/user-stories.txt
        Cahier des charges : 10 user stories priorisées MoSCoW,
        périmètre gelé, hors périmètre assumé
    docs/analyse/maquettes.txt
        Les 5 écrans : maquettes filaires, user story et endpoint
        associés à chaque écran
    docs/analyse/maquettes/
        Maquettes filaires (noir et blanc) des 5 écrans

Périmètre v1 — gelé
-------------------

Recherche de trajets, détail d'un trajet, inscription/connexion (JWT),
réservation de N places avec contrôle de disponibilité côté serveur,
« Mes réservations », annulation. Les trajets sont créés par un script de
peuplement (pas de page d'administration).

Hors périmètre (assumé) : paiement réel, e-mails, choix du siège, avis et
notes, multi-rôles, cartes, temps réel, connexion Google/Facebook.

Prochaines étapes
-----------------

- Semaine 2 : conception de la base de données (MCD, tables PostgreSQL,
  modèles SQLAlchemy, script de peuplement) et premiers endpoints Flask.
- Semaine 3 : API complète (authentification JWT, réservations) et
  première page Angular alimentée par de vraies données.
