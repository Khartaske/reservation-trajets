$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [Text.Encoding]::UTF8

$api = "http://localhost:5000/api"
$tmp = Join-Path $env:TEMP "scenario-api-reservation"
New-Item -ItemType Directory -Force $tmp | Out-Null

function Etape {
    param([string]$Titre)
    Write-Host ""
    Write-Host ("=== " + $Titre + " ===")
}

function Call-Api {
    param([string[]]$CurlArgs)
    Write-Host ("$ curl " + ($CurlArgs -join " "))
    $headerFile = Join-Path $tmp "derniers-entetes.txt"
    $body = (& curl.exe -s -D $headerFile @CurlArgs) -join "`n"
    $statusLine = Get-Content $headerFile -TotalCount 1
    Write-Host ("--> " + $statusLine)
    if ($body) { Write-Host $body }
    return $body
}

function Ecrire-Corps {
    param([hashtable]$Objet, [string]$Nom)
    $chemin = Join-Path $tmp $Nom
    $json = $Objet | ConvertTo-Json -Compress
    [IO.File]::WriteAllText($chemin, $json, (New-Object System.Text.UTF8Encoding $false))
    return $chemin
}

$horodatage = Get-Date -Format "yyyyMMddHHmmss"
$email = "voyageur$horodatage@example.fr"
$motDePasse = "motdepasse123"

Etape "Étape 1 — Inscription (POST /api/auth/register) : attendu 201"
$corps = Ecrire-Corps @{ email = $email; password = $motDePasse; full_name = "Voyageur Test" } "inscription.json"
$null = Call-Api @("-X", "POST", "$api/auth/register", "-H", "Content-Type: application/json", "--data-binary", "@$corps")

Etape "Étape 2 — Inscription avec le même email : attendu 409"
$null = Call-Api @("-X", "POST", "$api/auth/register", "-H", "Content-Type: application/json", "--data-binary", "@$corps")

Etape "Étape 3 — Connexion (POST /api/auth/login) : attendu 200 avec jeton + profil"
$corps = Ecrire-Corps @{ email = $email; password = $motDePasse } "connexion.json"
$reponse = Call-Api @("-X", "POST", "$api/auth/login", "-H", "Content-Type: application/json", "--data-binary", "@$corps")
$jeton = ($reponse | ConvertFrom-Json).token
$entAuth = "Authorization: Bearer $jeton"

Etape "Étape 4 — Profil sans jeton (GET /api/auth/me) : attendu 401"
$null = Call-Api @("$api/auth/me")

Etape "Étape 5 — Profil avec jeton (GET /api/auth/me) : attendu 200"
$null = Call-Api @("$api/auth/me", "-H", $entAuth)

Etape "Étape 6 — Recherche de trajets (GET /api/trips?origin=Paris) : attendu 200, trajets futurs triés"
$reponse = Call-Api @("$api/trips?origin=Paris")
$trajets = ($reponse | ConvertFrom-Json).trips
if (-not $trajets) {
    Etape "Repli — aucun trajet depuis Paris, liste complète (GET /api/trips)"
    $reponse = Call-Api @("$api/trips")
    $trajets = ($reponse | ConvertFrom-Json).trips
}
$trajet = $trajets[0]
$idTrajet = $trajet.id
Write-Host ""
Write-Host ("Trajet retenu pour la suite : id=" + $idTrajet + " (" + $trajet.origin + " -> " + $trajet.destination + ")")

Etape "Étape 7 — Détail du trajet avant réservation (GET /api/trips/$idTrajet) : attendu 200"
$reponse = Call-Api @("$api/trips/$idTrajet")
$placesAvant = ($reponse | ConvertFrom-Json).trip.remaining_seats
Write-Host ""
Write-Host ("Places restantes avant réservation : " + $placesAvant)

Etape "Étape 8 — Réservation de 2 places (POST /api/bookings) : attendu 201"
$corps = Ecrire-Corps @{ trip_id = $idTrajet; seats = 2 } "reservation.json"
$reponse = Call-Api @("-X", "POST", "$api/bookings", "-H", "Content-Type: application/json", "-H", $entAuth, "--data-binary", "@$corps")
$idReservation = ($reponse | ConvertFrom-Json).booking.id

Etape "Étape 9 — Tentative de sur-réservation (seats=9999) : attendu 409 avec message clair"
$corps = Ecrire-Corps @{ trip_id = $idTrajet; seats = 9999 } "surreservation.json"
$null = Call-Api @("-X", "POST", "$api/bookings", "-H", "Content-Type: application/json", "-H", $entAuth, "--data-binary", "@$corps")

Etape "Étape 10 — Mes réservations (GET /api/bookings) : attendu 200, avec infos du trajet"
$null = Call-Api @("$api/bookings", "-H", $entAuth)

Etape "Étape 11 — Annulation (DELETE /api/bookings/$idReservation) : attendu 200, statut -> cancelled"
$null = Call-Api @("-X", "DELETE", "$api/bookings/$idReservation", "-H", $entAuth)

Etape "Étape 12 — Mes réservations après annulation : le statut est « cancelled »"
$null = Call-Api @("$api/bookings", "-H", $entAuth)

Etape "Étape 13 — Détail du trajet après annulation : les places sont redevenues disponibles"
$reponse = Call-Api @("$api/trips/$idTrajet")
$placesApres = ($reponse | ConvertFrom-Json).trip.remaining_seats
Write-Host ""
Write-Host ("Places restantes avant réservation : " + $placesAvant + " | après annulation : " + $placesApres)
if ($placesApres -eq $placesAvant) {
    Write-Host "Vérifié : l'annulation a bien libéré les places (recalcul, aucun compteur stocké)."
} else {
    Write-Host "ATTENTION : les places restantes ne correspondent pas à la valeur initiale !"
}

Write-Host ""
Write-Host "Scénario terminé."
