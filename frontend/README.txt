Frontend Angular
================

Ce dossier contient l'application Angular 22 du projet « Réservation de
trajets ». Il a été généré avec Angular CLI (version 22.0.6) puis adapté
aux besoins du projet : composants standalone, CSS écrit à la main,
aucune bibliothèque d'interface externe.

Installation et lancement
-------------------------

Les instructions complètes (prérequis, base de données, API Flask et
frontend) se trouvent dans le README à la racine du dépôt. En résumé,
depuis ce dossier :

    npm install
    ng serve --port 4200

L'application est alors servie sur http://localhost:4200. Les appels vers
/api/... sont redirigés vers l'API Flask (port 5000) par proxy.conf.json :
aucun problème de CORS en développement.

Compilation de production
-------------------------

    ng build

Le résultat est produit dans le dossier dist/ ; c'est lui qui est publié
lors du déploiement.

Note : le projet n'utilise pas de framework de tests automatisés (choix
assumé, inscrit dans les limites du projet). La validation de l'API passe
par les scénarios de recette du dossier docs/, à la racine du dépôt.
