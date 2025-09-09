from flask import Flask
from flask_cors import CORS
import os


def create_app() -> Flask:
    app = Flask(__name__)

    # Configuration
    app.config["JSON_SORT_KEYS"] = False

    # CORS origins from env or defaults for Vite dev server
    allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    origins = [origin.strip() for origin in allowed_origins.split(",") if origin.strip()]

    CORS(app, resources={r"/api/*": {"origins": origins}})

    # Register blueprints
    from .api.routes import api_blueprint
    app.register_blueprint(api_blueprint, url_prefix="/api")

    return app
