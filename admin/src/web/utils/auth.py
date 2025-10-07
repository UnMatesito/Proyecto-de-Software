from functools import wraps

from flask import abort, flash, redirect, request, session, url_for

from core.services import get_user_by_id

# Funciones helper


def get_current_user():
    """
    Obtiene el usuario actual desde la sesión activa.

    Returns:
        User | None: Usuario autenticado o None si no hay sesión.
    """
    if "user_id" in session:
        return get_user_by_id(session["user_id"])
    return None


# Decoradores


def login_required(f):
    """Decorador que exige que el usuario esté autenticado antes de acceder a una ruta."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Debe iniciar sesión para acceder a esta página", "warning")
            return redirect(url_for("auth.login", next=request.url))

        # Verificar que el usuario existe y puede hacer login
        user = get_current_user()
        if not user:
            session.clear()
            flash("Usuario no encontrado. Por favor, inicie sesión nuevamente", "error")
            return redirect(url_for("auth.login"))

        if not user.is_active():
            session.clear()
            flash("Su cuenta ha sido deshabilitada", "error")
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)

    return decorated_function


def permission_required(permission_name):
    """
    Decorador que valida que el usuario tenga un permiso específico.

    Args:
        permission_name (str): Nombre del permiso requerido.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                abort(401)

            user = get_current_user()
            if not user or not user.is_active():
                session.clear()
                abort(401)

            # System Admin puede hacer todo sin importar permisos
            if user.system_admin:
                return f(*args, **kwargs)

            if not user.has_permission(permission_name):
                abort(403)  # Forbidden

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def role_required(role_name):
    """
    Decorador que valida que el usuario tenga un rol específico.

    Args:
        role_name (str): Nombre del rol requerido.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                abort(401)

            user = get_current_user()
            if not user or not user.is_active():
                abort(401)

            # System Admin puede hacer todo sin importar roles
            if user.system_admin:
                return f(*args, **kwargs)

            if not user.has_role(role_name):
                abort(403)  # Forbidden

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def system_admin_required(f):
    """Decorador que permite acceso solo a usuarios con flag System Admin."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            abort(401)

        user = get_current_user()
        if not user or not user.is_active():
            session.clear()
            abort(401)

        if not user.system_admin:
            abort(403)

        return f(*args, **kwargs)

    return decorated_function


# Funciones para jinja2


def is_authenticated():
    """
    Indica si existe un usuario autenticado en la sesión.

    Returns:
        bool: True si hay sesión activa, False en caso contrario.
    """
    return "user_id" in session


def is_system_admin():
    """
    Indica si el usuario autenticado es System Admin.

    Returns:
        bool: True si es administrador del sistema, False en caso contrario.
    """
    if "user_id" not in session:
        return False
    user = get_current_user()
    return bool(user and user.system_admin)


def get_user_role_name(user_id):
    """
    Obtiene el nombre del rol del usuario o 'Administrador del sistema' si corresponde.

    Args:
        user_id (int): ID del usuario.

    Returns:
        str: Nombre del rol o None si el usuario no existe.
    """
    user = get_user_by_id(user_id)
    if not user:
        return None
    if user.is_admin():
        return "Administrador del sistema"
    if user.role:
        return user.role.name
    return None


def has_permission(permission_name: str) -> bool:
    """
    Determina si el usuario actual tiene un permiso específico.

    Args:
        permission_name (str): Nombre del permiso.

    Returns:
        bool: True si tiene el permiso, False en caso contrario.
    """
    if "user_id" not in session:
        return False
    user = get_current_user()
    if not user or not user.is_active():
        return False
    # System Admin siempre tiene todos los permisos
    if user.system_admin:
        return True
    return user.has_permission(permission_name)


def is_validated_site(site):
    """
    Determina si un sitio histórico está validado.

    Args:
        site (HistoricSite): Sitio histórico a evaluar.

    Returns:
        bool: True si el sitio está validado, False si está pendiente.
    """
    return site and not site.pending_validation
