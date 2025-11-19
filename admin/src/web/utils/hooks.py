from flask import jsonify, redirect, render_template, request, session, url_for

from core.services import get_feature_flag_by_name, get_user_by_id

EXEMPT_PATHS = ["/static/", "/auth/"]
EXEMPT_ENDPOINTS = [
    "auth.login",
    "auth.logout",
    "auth.authenticate",
    "main_bp.maintenance",
]


def _is_api_request():
    """Determina si la solicitud actual proviene del blueprint de la API."""
    return request.blueprint == "api" or request.path.startswith("/api")


def _api_maintenance_response(message):
    """Respuesta JSON estándar cuando la API no está disponible."""
    return (
        jsonify(
            {
                "error": {
                    "code": "service_unavailable",
                    "message": message,
                }
            }
        ),
        503,
    )


def hook_admin_maintenance():
    """Bloquea la administración si el flag admin_maintenance está ON, menos al system admin"""
    flag = get_feature_flag_by_name("admin_maintenance_mode")

    # Si el flag no existe o está apagado, no bloquear nada
    if not flag or not flag.is_enabled:
        return

    # Excluir rutas estáticas o auth
    if any(request.path.startswith(p) for p in EXEMPT_PATHS):
        return
    if request.endpoint in EXEMPT_ENDPOINTS:
        return

    # Permitir acceso a system admins
    user_id = session.get("user_id")
    user = get_user_by_id(user_id) if user_id else None
    if user and user.is_admin():
        return

    message = (
        flag.maintenance_message
        or "La API no está disponible porque el administrador está en mantenimiento."
    )

    # Cuando la solicitud proviene de la API, devolvemos un JSON
    if _is_api_request():
        return _api_maintenance_response(message)

    # Para el panel administrativo, redirigimos a la vista de mantenimiento
    return redirect(url_for("main_bp.maintenance"))


def hook_portal_maintenance():
    """Verifica el estado del flag portal_maintenance, en caso de estar on y no ser system admin, redirige"""
    flag = get_feature_flag_by_name("portal_maintenance_mode")

    if flag and flag.is_enabled:
        user_id = session.get("user_id")
        user = get_user_by_id(user_id) if user_id else None

        if not (user and user.is_admin()):
            message = (
                flag.maintenance_message
                or "La API no está disponible porque el portal está en mantenimiento."
            )
            return _api_maintenance_response(message)


def hook_reviews_enabled():
    """Verifica el estado del flag  reviews_enabled, en caso de estar on y no ser system admin, redirige"""
    flag = get_feature_flag_by_name("reviews_enabled")

    if flag and flag.is_enabled:
        user_id = session.get("user_id")
        user = get_user_by_id(user_id) if user_id else None

        if not (user and user.is_admin()):
            return (
                render_template("maintenance.html", message=flag.maintenance_message),
                503,
            )
