import re

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import User, db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Corps JSON manquant ou invalide."}), 400

    email = str(data.get("email") or "").strip().lower()
    password = str(data.get("password") or "")
    full_name = str(data.get("full_name") or "").strip()

    if not email or not password or not full_name:
        return (
            jsonify(
                {"error": "Les champs email, password et full_name sont obligatoires."}
            ),
            400,
        )
    if not EMAIL_RE.match(email) or len(email) > 255:
        return jsonify({"error": "L'adresse email est invalide."}), 400
    if len(password) < 8:
        return (
            jsonify({"error": "Le mot de passe doit contenir au moins 8 caractères."}),
            400,
        )
    if len(full_name) > 100:
        return (
            jsonify({"error": "Le nom complet ne doit pas dépasser 100 caractères."}),
            400,
        )

    existing = db.session.execute(
        db.select(User).where(User.email == email)
    ).scalar_one_or_none()
    if existing is not None:
        return (
            jsonify({"error": "Un compte existe déjà avec cette adresse email."}),
            409,
        )

    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        full_name=full_name,
    )
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return (
            jsonify({"error": "Un compte existe déjà avec cette adresse email."}),
            409,
        )

    return jsonify({"user": user.to_dict()}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Corps JSON manquant ou invalide."}), 400

    email = str(data.get("email") or "").strip().lower()
    password = str(data.get("password") or "")
    if not email or not password:
        return (
            jsonify({"error": "Les champs email et password sont obligatoires."}),
            400,
        )

    user = db.session.execute(
        db.select(User).where(User.email == email)
    ).scalar_one_or_none()
    if user is None or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Email ou mot de passe incorrect."}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()}), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    user = db.session.get(User, int(get_jwt_identity()))
    if user is None:
        return jsonify({"error": "Utilisateur introuvable."}), 404
    return jsonify({"user": user.to_dict()}), 200
