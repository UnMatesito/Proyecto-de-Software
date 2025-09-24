from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from core.services import user_service
from core.utils.auth import login_required

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.get("/")
def login():
    """Renderiza la página de inicio de sesión.

    Returns:
        Response: Página de login.
    """
    return render_template("auth/login.html")


@bp.post("/login")
def authenticate():
    """
    Autentica al usuario y crea una sesión.
    Valida las credenciales del usuario y crea una sesión activa
    si la autenticación es exitosa.

    Returns:
        Redirección al sistema de administración si es exitoso,
        o al login con mensaje de error si falla.
    """
    email = request.form["email"].strip()
    password = request.form["password"]

    if not email or not password:
        flash("Email y contraseña son obligatorios", "error")
        return redirect(url_for("auth.login"))

    user = user_service.get_user_by_email(email)

    if user is None or not user.check_password(password):
        flash("Email y/o contraseña incorrectos", "error")
        return redirect(url_for("auth.login"))
    session["user_id"] = user.id
    return redirect(url_for("home"))


@bp.get("/logout")
@login_required
def logout():
    """Cierra la sesión del usuario.
    Borra la sesión y redirige a la página de inicio de sesión.

    Returns:
        Response: Redirección al login con mensaje de éxito.
    """
    session.clear()
    flash("Has cerrado sesión", "success")
    return redirect(url_for("auth.login"))
