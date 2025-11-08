from marshmallow import Schema, fields, validate
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError


class ReviewCreateSchema(Schema):
    """Valida la creación de reseñas (POST)."""
    rating = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=5),
        error_messages={"required": "This field is required"}
    )
    comment = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=1000),
        error_messages={"required": "This field is required"}
    )


class ReviewQuerySchema(Schema):
    """Valida los parámetros de consulta de reseñas (GET)."""
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=10, validate=validate.Range(min=1, max=100))
    order_by = fields.Str(load_default="created_at")
    sorted_by = fields.Str(validate=validate.OneOf(["asc", "desc"]), load_default="desc")

class ReviewResponseSchema(Schema):
    """Serializa reseñas en las respuestas de la API."""
    id = fields.Int()
    site_id = fields.Int(attribute="historic_site_id")
    rating = fields.Int()
    comment = fields.Str(attribute="content")
    inserted_at = fields.Method("get_inserted_at")
    updated_at = fields.Method("get_updated_at")

    # Reseña pertenece al usuario actual
    isUserReview = fields.Method("get_is_user_review")

    def get_inserted_at(self, obj):
        return obj.created_at.isoformat() + "Z" if obj.created_at else None

    def get_updated_at(self, obj):
        return obj.updated_at.isoformat() + "Z" if obj.updated_at else None

    def get_is_user_review(self, obj):
        """
        Devuelve True si el usuario autenticado es el dueño de esta reseña.
        Si no hay JWT o no es válido, devuelve False sin romper la ejecución.
        """
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            return current_user_id == getattr(obj, "user_id", None)
        except NoAuthorizationError:
            # No había token en la request → usuario no autenticado
            return False
        except Exception:
            # Cualquier otro error (token mal formado, etc.)
            return False

