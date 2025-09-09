from flask import Blueprint, jsonify

api_blueprint = Blueprint("api", __name__)

@api_blueprint.get("/")
def index():
    return jsonify({"message": "A-Impact Licensing Assistant API"})

@api_blueprint.get("/health")
def health_check():
    return jsonify({"status": "ok"})
