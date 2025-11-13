from marshmallow import Schema, fields, validate

from .sites_schemas import HistoricSiteShortSchema


class ReviewCreateSchema(Schema):
    """Valida la creación de reseñas (POST)."""

    rating = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=5),
        error_messages={"required": "This field is required"},
    )
    comment = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=1000),
        error_messages={"required": "This field is required"},
    )


class ReviewQuerySchema(Schema):
    """Valida los parámetros de consulta de reseñas (GET)."""

    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=10, validate=validate.Range(min=1, max=100))
    order_by = fields.Str(load_default="created_at")
    sorted_by = fields.Str(
        validate=validate.OneOf(["asc", "desc"]), load_default="desc"
    )


class ReviewResponseSchema(Schema):
    """Serializa reseñas en las respuestas de la API."""

    id = fields.Int()
    site_id = fields.Int(attribute="historic_site_id")
    rating = fields.Int()
    comment = fields.Str(attribute="content")
    inserted_at = fields.Method("get_inserted_at")
    updated_at = fields.Method("get_updated_at")

    def get_inserted_at(self, obj):
        return obj.created_at.isoformat() + "Z" if obj.created_at else None

    def get_updated_at(self, obj):
        return obj.updated_at.isoformat() + "Z" if obj.updated_at else None


class MyReviewQuerySchema(Schema):
    """Valida los parámetros de consulta para las reseñas del perfil del usuario."""

    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(
        load_default=25,
        validate=validate.OneOf([25, 50, 100]),
    )
    sort = fields.Str(
        load_default="date_desc",
        validate=validate.OneOf(["date_desc", "date_asc"]),
    )


class MyReviewResponseSchema(Schema):
    """Serializa reseñas para la página de ""Mi Perfil""."""

    id = fields.Int()
    rating = fields.Int()
    comment = fields.Str(attribute="content")
    inserted_at = fields.Method("get_inserted_at")

    historic_site = fields.Nested(
        HistoricSiteShortSchema,
        attribute="historic_site",
        data_key="site",
    )

    def get_inserted_at(self, obj):
        return obj.created_at.isoformat() + "Z" if obj.created_at else None
