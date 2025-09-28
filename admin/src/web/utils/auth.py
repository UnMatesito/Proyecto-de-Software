from functools import wraps

from flask import abort, flash, redirect, request, session, url_for

from core.services import get_user_by_id

# Funciones helper


def get_current_user():
    """Obtiene el usuario actual de la sesión"""
    if "user_id" in session:
        return get_user_by_id(session["user_id"])
    return None


# Decoradores


def login_required(f):
    """Decorador que requiere que el usuario esté logueado"""

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
    """Decorador que requiere un permiso específico"""

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
    """Decorador que requiere un rol específico"""

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
    """Decorador que requiere que el usuario sea System Admin"""

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


"""
def check_maintenance_mode():
    Verifica si el modo mantenimiento está activo
    try:
        flag = FeatureFlag.query.filter_by(name="admin_maintenance_mode").first()
        if flag and flag.is_enabled:
            # Solo permitir acceso a System Admins
            if "user_id" in session:
                user = User.query.get(session["user_id"])
                if user and user.system_admin:
                    return False, None
            return True, flag.maintenance_message
        return False, None
    except SQLAlchemyError:
        # Error al consultar la base de datos, asumir que no está en mantenimiento
        return False, None
    except Exception:
        # Cualquier otro error, asumir que no está en mantenimiento
        return False, None
"""

# Funciones para jinja2


def is_authenticated():
    """Devuelve true si el usuario tiene la sesión iniciada"""
    return session["user_id"] is not None

def is_system_admin():
    """Devuelve True si el usuario actual es System Admin"""
    if "user_id" not in session:
        return False
    user = get_current_user()
    return bool(user and user.system_admin)


def get_user_role_name(user_id):
    """Obtiene el nombre del rol del usuario dado su ID.
    Si es System Admin, devuelve 'Administrador del sistema'."""
    user = get_user_by_id(user_id)
    if not user:
        return None
    if user.is_admin():
        return "Administrador del sistema"
    if user.role:
        return user.role.name
    return None


def has_permission(permission_name: str) -> bool:
    """Devuelve True si el usuario actual tiene el permiso dado"""
    if "user_id" not in session:
        return False
    user = get_current_user()
    if not user or not user.is_active():
        return False
    # System Admin siempre tiene todos los permisos
    if user.system_admin:
        return True
    return user.has_permission(permission_name)
