import flask
import werkzeug
from flask import request, jsonify, current_app, redirect, session, url_for
from web import oauth

from authlib.integrations.base_client.errors import AuthlibBaseError
from urllib.parse import urlencode
from datetime import timedelta
from flask_jwt_extended import create_access_token, jwt_required, unset_jwt_cookies, set_access_cookies
from core.models.user import User
from core.services import user_service
from . import api_bp

@api_bp.route("/auth/google/login")
def google_login() -> werkzeug.Response:
    """Redirige al usuario a Google para autenticarse."""
    print(flask.request.args.get('state'), flask.session.get('_google_authlib_state_'))

    redirect_uri = current_app.config['GOOGLE_REDIRECT_URI']

    print(f"DEBUG: Google Redirect URI usada: {redirect_uri}")
    return oauth.google.authorize_redirect(redirect_uri)


@api_bp.route("/auth/google/callback")
def google_callback():
    """Callback de Google. Procesa la respuesta y genera JWT (CORREGIDO)."""
    error_message = "Error durante la autenticación con Google." 
    frontend_redirect_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:5173')}/login"

    try:
        token = oauth.google.authorize_access_token()
        if not token:
            error_message = "No se recibió token de autorización de Google."
            raise AuthlibBaseError(error='token_missing', description=error_message)

        user_info = oauth.google.userinfo(token=token)

        if not user_info or not user_info.get('email'):
             error_message = "No se pudo obtener información válida del usuario desde Google."
             raise ValueError(error_message) 

        user = user_service.find_or_create_google_user(user_info)

        expires_delta = current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES", timedelta(hours=1))
        access_token = create_access_token(identity=str(user.id), expires_delta=expires_delta)

        frontend_callback_url_ok = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:5173')}/auth/callback"
        response = redirect(frontend_callback_url_ok)
        set_access_cookies(response, access_token, max_age=expires_delta)
        
        print(f"DEBUG: Google Auth OK. Seteando cookie JWT y redirigiendo a frontend.")

        return response

    except ValueError as e: 
        error_code = "user_issue"
        error_message = str(e)
        print(f"ERROR (ValueError) en callback de Google: {e}")
    except AuthlibBaseError as e:
        error_code = e.error if hasattr(e, 'error') else "oauth_error"
        error_message = f"{e.description}" if hasattr(e, 'description') else str(e)
        print(f"ERROR (Authlib) en callback de Google: {e}")
    except Exception as e:
        error_code = "internal_error"
        print(f"ERROR (Inesperado) en callback de Google: {e}")
        error_message = "Ocurrió un error inesperado durante la autenticación." 

    error_params = urlencode({'error': error_code, 'message': error_message})
    return redirect(f"{frontend_redirect_url}?{error_params}")


@api_bp.route("/auth/google/logout", methods=["POST"]) 
@jwt_required()
def google_logout():
    """Cierra la sesión del usuario en Google."""
    session.clear()
    response = jsonify({"message": "Google logout successful"})
    unset_jwt_cookies(response)
    return response
