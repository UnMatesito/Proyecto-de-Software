from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from core.services.feature_flag_service import (
    get_all_feature_flags_ordered_by_id,
    get_feature_flag_by_id,
    set_maintenance_message,
    toggle_feature_flag,
)
from core.services.user_service import get_user_by_id
from web.forms.feature_flag import ToggleFeatureFlagForm
from web.utils.auth import login_required, system_admin_required

feature_flag_bp = Blueprint("feature-flags", __name__, url_prefix="/feature-flag")


@feature_flag_bp.get("/")
@login_required
@system_admin_required
def index():
    flags = get_all_feature_flags_ordered_by_id()
    form = ToggleFeatureFlagForm()
    return render_template("feature_flags/index.html", flags=flags, form=form)


@feature_flag_bp.post("/<int:flag_id>/toggle")
@login_required
@system_admin_required
def toggle(flag_id):
    """Cambiar el estado de un flag"""
    user = get_user_by_id(session["user_id"])
    form = ToggleFeatureFlagForm()
    flag = get_feature_flag_by_id(flag_id)
    new_state = not flag.is_enabled
    # Si es de tipo mantenimiento y el nuevo estado es activado y no tiene mensaje
    if flag.is_maintenance() and new_state:
        if not form.validate_on_submit() or not form.message.data.strip():
            flash(
                "Debe ingresar un mensaje de mantenimiento (máx. 255 caracteres)",
                "error",
            )
            return redirect(url_for("feature-flags.index"))
        set_maintenance_message(flag_id, form.message.data.strip())

    toggle_feature_flag(flag_id, new_state, user)
    flash(
        f"Flag '{flag.description}' cambiado a {'ON' if new_state else 'OFF'}",
        "success",
    )
    return redirect(url_for("feature-flags.index"))
