from flask import Blueprint, render_template

from core.services import get_feature_flag_by_name

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


@main_bp.get("/maintenance")
def maintenance():
    """Vista pública que muestra el mensaje de mantenimiento del admin."""
    flag = get_feature_flag_by_name("admin_maintenance_mode")
    message = flag.maintenance_message if flag else None
    message = message or "El panel administrativo está en mantenimiento."
    return render_template("maintenance.html", message=message), 503