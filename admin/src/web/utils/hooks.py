from flask import render_template, session

from core.services import get_feature_flag_by_name, get_user_by_id


def hook_admin_maintenance():
    """Verifica el estado del flag admin_maintenance, en caso de estar on y no ser system admin, redirige"""
    flag = get_feature_flag_by_name("admin_maintenance_mode")

    if flag and flag.is_enabled:
        user_id = session.get("user_id")
        user = get_user_by_id(user_id) if user_id else None

        if not (user and user.is_admin()):
            return (
                render_template("maintenance.html", message=flag.maintenance_message),
                503,
            )


def hook_portal_maintenance():
    """Verifica el estado del flag portal_maintenance, en caso de estar on y no ser system admin, redirige"""
    flag = get_feature_flag_by_name("portal_maintenance_mode")

    if flag and flag.is_enabled:
        user_id = session.get("user_id")
        user = get_user_by_id(user_id) if user_id else None

        if not (user and user.is_admin()):
            return (
                render_template("maintenance.html", message=flag.maintenance_message),
                503,
            )


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
