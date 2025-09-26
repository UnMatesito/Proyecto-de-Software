from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from core.services.feature_flag_service import (
    get_all_feature_flags,
    get_feature_flag_by_id,
    set_maintenance_message,
    toggle_feature_flag,
)
from core.services.user_service import get_user_by_id
from web.utils.auth import login_required, system_admin_required

feature_flag_bp = Blueprint("feature-flags", __name__, url_prefix="/feature-flag")


@login_required
@system_admin_required
@feature_flag_bp.route("/")
def index():
    flags = get_all_feature_flags()
    return render_template("feature_flags/index.html", flags=flags)


@login_required
@system_admin_required
@feature_flag_bp.route("/<int:flag_id>/toggle", methods=["POST"])
def toggle(flag_id):
    user = get_user_by_id(session["user_id"])
    flag = get_feature_flag_by_id(flag_id)
    new_state = not flag.is_enabled
    if flag.is_maintenance() and new_state:
        message = request.form.get("message", "").strip()
        if not message:
            flash("Debe ingresar un mensaje de mantenimiento", "error")
            return redirect(url_for("feature-flags.index"))
        if len(message) > 255:
            flash("El mensaje no puede superar los 255 caracteres", "error")
            return redirect(url_for("feature-flags.index"))
        set_maintenance_message(flag_id, message, user)

    toggle_feature_flag(flag_id, new_state)
    flash(
        f"Flag '{flag.description}' cambiado a {'ON' if new_state else 'OFF'}",
        "success",
    )
    return redirect(url_for("feature-flags.index"))
