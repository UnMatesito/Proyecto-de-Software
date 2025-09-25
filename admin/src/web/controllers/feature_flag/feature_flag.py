from flask import Blueprint, render_template, request, redirect, url_for, flash
from core.services.feature_flag_service import (
    get_all_feature_flags,
    get_feature_flag_by_id,
    set_maintenance_message
    
)




feature_flag_bp = Blueprint('feature-flag', __name__, url_prefix='/feature-flag')

@feature_flag_bp.route("/")
def index():
    flags = get_all_feature_flags()
    return render_template("feature_flags/index.html",flags=flags)

@feature_flag_bp.route("/<int:flag_id>/toggle", methods=["POST"])
def toggle_feature_flag(flag_id):

    flag = get_feature_flag_by_id(flag_id)
    is_enable = not flag.is_enble

    if flag.is_maintenance and is_enable:
        message = request.get("message","").strip()
        if not message:
            flash("Debe ingresar un mensaje de mantenimiento","error")
            return redirect(url_for("feature_flags.index"))
        if len(message)  > 255:
            flash("El mensaje no puede superar los 255 caracteres","error")
            return redirect(url_for("feature_flags.index"))
        set_maintenance_message(flag_id,message)
    
    toggle_feature_flag(flag_id, is_enable)
    flash(f"Flag '{flag.description}' cambiado a {'ON' if is_enable else 'OFF'}", "success")
    return redirect(url_for("feature_flags.index"))

    