import os
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")

    app.config["JWT_SECRET_KEY"] = app.config["SECRET_KEY"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

    app.json.ensure_ascii = False

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from app.models import db

    db.init_app(app)

    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def handle_missing_token(reason: str):
        return jsonify({"error": "Jeton d'authentification manquant."}), 401

    @jwt.invalid_token_loader
    def handle_invalid_token(reason: str):
        return jsonify({"error": "Jeton d'authentification invalide."}), 401

    @jwt.expired_token_loader
    def handle_expired_token(jwt_header, jwt_payload):
        return jsonify({"error": "Le jeton d'authentification a expiré."}), 401

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"error": "Ressource introuvable."}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({"error": "Méthode non autorisée pour cette route."}), 405

    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({"error": "Erreur interne du serveur."}), 500

    from app.routes.auth import auth_bp
    from app.routes.bookings import bookings_bp
    from app.routes.health import health_bp
    from app.routes.trips import trips_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(trips_bp)
    app.register_blueprint(bookings_bp)

    return app
