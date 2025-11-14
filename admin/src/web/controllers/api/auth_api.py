import os
from datetime import timedelta
from urllib.parse import urlencode

from authlib.integrations.base_client.errors import AuthlibBaseError
from flask import current_app, jsonify, redirect, request, session, url_for
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    set_access_cookies,
    unset_jwt_cookies,
)

from core.models.user import User
from core.services import user_service

if os.getenv("FLASK_ENV") == "development":
    from web import oauth
else:
    from src.web import oauth

from . import api_bp


@api_bp.route("/auth/google/login")
def google_login():
    """Redirige al usuario a Google para autenticarse."""
    redirect_uri = current_app.config["GOOGLE_REDIRECT_URI"]

    next_url = request.args.get("next", "/")
    session["next_url"] = next_url

    print(f"DEBUG: Google Redirect URI usada: {redirect_uri}, next= {next_url}")
    return oauth.google.authorize_redirect(redirect_uri)


@api_bp.route("/auth/google/callback")
def google_callback():
    """
    Callback de Google. Maneja la respuesta de Google después de la autenticación.
    Crea o encuentra al usuario en la base de datos y genera un token JWT.
    Redirige al frontend con el token o un código de error.
    """

    frontend_base = current_app.config.get(
        "FRONTEND_URL", "https://grupo09.proyecto2025.linti.unlp.edu.ar/"
    )

    if "error" in request.args and request.args.get("error") == "access_denied":
        print("DEBUG: El usuario canceló el login de Google.")
        error_params = urlencode({"error_code": "cancelled"})
        return redirect(f"{frontend_base}/?{error_params}")

    try:
        token = oauth.google.authorize_access_token()

        if not token:
            raise AuthlibBaseError(
                error="tokenmissing",
                description="No se pudo obtener el token de acceso de Google.",
            )

        user_info = oauth.google.userinfo(token=token)
        user = user_service.find_or_create_google_user(user_info)

        if not user.is_active():
            print(f"DEBUG: Usuario inactivo (bloqueado o borrado): {user.id}")
            error_params = urlencode({"error_code": "user_blocked"})
            return redirect(f"{frontend_base}/?{error_params}")

        next_url = session.pop("next_url", "/")
        if not next_url.startswith("/"):
            next_url = "/"

        expires_delta = current_app.config.get(
            "JWT_ACCESS_TOKEN_EXPIRES", timedelta(hours=24)
        )
        access_token = create_access_token(
            identity=str(user.id), expires_delta=expires_delta
        )

        response = redirect(frontend_base + next_url)
        set_access_cookies(response, access_token, max_age=expires_delta)
        return response

    except ValueError as e:
        if "inactivo o bloqueado" in str(e):
            print(f"DEBUG: Usuario bloqueado detectado por ValueError: {e}")
            error_params = urlencode({"error_code": "user_blocked"})
            return redirect(f"{frontend_base}/?{error_params}")
        else:
            print(f"ERROR (ValueError) en callback Google: {e}")
            error_params = urlencode({"error_code": "unknown_failure"})
            return redirect(f"{frontend_base}/?{error_params}")

    except Exception as e:
        print(f"ERROR en callback Google: {e}")
        error_params = urlencode({"error_code": "unknown_failure"})
        return redirect(f"{frontend_base}/?{error_params}")


@api_bp.route("/auth/google/logout", methods=["POST"])
@jwt_required()
def google_logout():
    """Cierra la sesión del usuario en Google."""
    session.clear()
    response = jsonify({"message": "Google logout successful"})
    unset_jwt_cookies(response)
    return response
