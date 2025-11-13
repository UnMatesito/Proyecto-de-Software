from flask import jsonify

from core.services import get_feature_flag_by_name

from . import api_bp


@api_bp.get("/feature-flags/<string:flag_name>")
def get_feature_flag(flag_name):
    """Retorna el estado del flag y el mensaje de mantenimiento."""

    flag = get_feature_flag_by_name(flag_name)

    if not flag:
        return (
            jsonify(
                {
                    "error": {
                        "code": "not_found",
                        "message": "Feature flag not found",
                    }
                }
            ),
            404,
        )

    return (
        jsonify(
            {
                "name": flag.name,
                "is_enabled": bool(flag.is_enabled),
                "maintenance_message": flag.maintenance_message or "",
            }
        ),
        200,
    )