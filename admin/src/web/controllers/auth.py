from flask import Blueprint, flash, redirect, render_template, session, url_for

from core.services import user_service
from web.utils.auth import login_required
from web.forms.auth import AuthForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.get("/")
def login():
    """
    Renderiza la página de inicio de sesión.

    Crea una instancia vacía del formulario de autenticación (`AuthForm`)
    y la pasa a la plantilla para que el usuario pueda ingresar sus
    credenciales.

    Returns:
        Response: Página HTML del formulario de login.
    """
    form = AuthForm()
    return render_template("auth/login.html", form=form)


@auth_bp.post("/login")
def authenticate():
    """
    Autentica al usuario y crea una sesión activa.

    Valida las credenciales enviadas a través del formulario de login.
    Si son correctas, guarda el ID del usuario en la sesión y redirige
    a la página principal. Si son incorrectas o el formulario no es válido,
    vuelve a renderizar la página de login con un mensaje de error.

    Returns:
        Response: 
            - Si la autenticación es exitosa, redirige a la vista 'home'.
            - Si falla, renderiza nuevamente la plantilla de login con errores.
    """
    form = AuthForm()

    if not form.validate_on_submit():  
        return render_template("auth/login.html", form=form)

    email = form.email.data
    user = user_service.get_user_by_email(email)

    if user is None or not user.check_password(form.password.data):
        flash("Email y/o contraseña incorrectos", "error")
        return render_template("auth/login.html", form=form)
        
    session["user_id"] = user.id
    return redirect(url_for("home"))


@auth_bp.get("/logout")
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
