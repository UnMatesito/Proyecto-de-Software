from flask import Blueprint, render_template

from web.utils.auth import get_current_user, login_required

main_bp = Blueprint("main_bp", __name__)


@main_bp.route("/")
@login_required
def home():
    """Página principal después de login"""
    return render_template("home.html")


@main_bp.route("/profile")
@login_required
def profile():
    """Perfil del usuario autenticado"""
    user = get_current_user()
    return render_template("users/detail.html", user=user)
