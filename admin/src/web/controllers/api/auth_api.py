from flask import request, jsonify
from flask_jwt_extended import create_access_token
from core.models.user import User
from . import api_bp


@api_bp.post("/auth")
def login():
    """
    POST /api/auth
    Autentica un usuario con email y contraseña y devuelve un token JWT.

    Según PDF:
    - Campo: "user" (no "email")
    - Respuesta: "token" y "expires_in"
    - Error 401: código "invalid_credentials"
    """
    data = request.get_json() or {}

    # Según el PDF, el campo se llama "user" (que contiene el email)
    user_email = data.get("user")
    password = data.get("password")

    # Validar que los campos estén presentes
    if not user_email or not password:
        return jsonify({
            "error": {
                "code": "invalid_data",
                "message": "User and password are required",
                "details": {
                    "user": ["This field is required"] if not user_email else [],
                    "password": ["This field is required"] if not password else []
                }
            }
        }), 400

    # Buscar usuario por email
    user = User.query.filter_by(email=user_email).first()

    # Validar credenciales
    if not user or not user.check_password(password):
        return jsonify({
            "error": {
                "code": "invalid_credentials",
                "message": "Credenciales inválidas."
            }
        }), 401

    # Generar token JWT con expiración de 1 hora (3600 segundos)
    token = create_access_token(identity=user.id)
    expires_in = 3600  # 1 hora en segundos

    # Respuesta según el formato del PDF
    return jsonify({
        "token": token,
        "expires_in": expires_in
    }), 200