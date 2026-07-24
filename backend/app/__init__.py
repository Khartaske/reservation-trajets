import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")

    app.json.ensure_ascii = False

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from app.models import db

    db.init_app(app)

    from app.routes.health import health_bp
    from app.routes.trips import trips_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(trips_bp)

    return app
