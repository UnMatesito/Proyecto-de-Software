"""
Schemas de validación para la API de Sitios Históricos usando Marshmallow
"""
from datetime import datetime, timezone

from marshmallow import Schema, fields, validates, ValidationError, validate, validates_schema
from core.services import conservation_state_service


class SiteQuerySchema(Schema):
    """Schema para validar parámetros de query en GET /sites"""

    name = fields.Str()
    description = fields.Str()
    city = fields.Str()
    province = fields.Str()
    tags = fields.Str()  # Será parseado como CSV
    order_by = fields.Str(
        validate=validate.OneOf(["latest", "oldest", "rating-5-1", "rating-1-5"]),
        load_default="latest"
    )
    lat = fields.Float(validate=validate.Range(min=-90, max=90))
    long = fields.Float(validate=validate.Range(min=-180, max=180))
    radius = fields.Float(validate=validate.Range(min=0))
    page = fields.Int(validate=validate.Range(min=1), load_default=1)
    per_page = fields.Int(validate=validate.Range(min=1, max=100), load_default=20)

    @validates_schema
    def validate_geospatial(self, data, **kwargs):
        """Valida que si se usa búsqueda geoespacial, todos los parámetros estén presentes"""
        geo_fields = ['lat', 'long', 'radius']
        geo_provided = [field for field in geo_fields if field in data and data[field] is not None]

        if geo_provided and len(geo_provided) != 3:
            missing = [f for f in geo_fields if f not in geo_provided]
            raise ValidationError(
                f"When using geospatial search, all parameters are required: {', '.join(geo_fields)}",
                field_name=missing[0] if missing else 'lat'
            )


class SiteCreateSchema(Schema):
    """Schema para validar datos al crear un sitio histórico"""

    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255),
        error_messages={"required": "This field is required"}
    )
    short_description = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={"required": "This field is required"}
    )
    description = fields.Str(
        required=True,
        validate=validate.Length(min=1),
        error_messages={"required": "This field is required"}
    )
    city = fields.Str(
        required=True,
        error_messages={"required": "This field is required"}
    )
    province = fields.Str(
        required=True,
        error_messages={"required": "This field is required"}
    )
    country = fields.Str(
        required=True,
        validate=validate.Length(equal=2),
        error_messages={"required": "This field is required"}
    )
    lat = fields.Float(
        required=True,
        validate=validate.Range(min=-90, max=90),
        error_messages={
            "required": "This field is required",
            "invalid": "Must be a valid latitude between -90 and 90"
        }
    )
    long = fields.Float(
        required=True,
        validate=validate.Range(min=-180, max=180),
        error_messages={
            "required": "This field is required",
            "invalid": "Must be a valid longitude between -180 and 180"
        },
        data_key="long"
    )
    tags = fields.List(
        fields.Str(),
        required=True,
        validate=validate.Length(min=1),
        error_messages={"required": "This field is required"}
    )
    state_of_conservation = fields.Str(
        required=True,
        error_messages={"required": "This field is required"}
    )
    inauguration_year = fields.Int(
        required=True,
        validate=validate.Range(min=1000, max=datetime.now(timezone.utc).year),
        load_default=2000,
        error_messages={"required": "This field is required", "invalid": "Must be an integer between 1000 and the current year"}
    )
    category = fields.Str(
        required=True,
        allow_none=True)

    @validates('state_of_conservation')
    def validate_conservation_state(self, value):
        """Valida que el estado de conservación exista usando el servicio"""
        try:
            valid_states = conservation_state_service.get_all_conservation_state()
            valid_state_names = [state.state for state in valid_states]

            if value not in valid_state_names:
                raise ValidationError(
                    f"Must be one of: {', '.join(valid_state_names)}"
                )
        except ValueError as e:
            raise ValidationError(str(e))

    @validates('tags')
    def validate_tags(self, value):
        """Valida que tags sea una lista no vacía"""
        if not isinstance(value, list):
            raise ValidationError("Tags must be a list")
        if len(value) == 0:
            raise ValidationError("At least one tag is required")
        for tag in value:
            if not isinstance(tag, str) or not tag.strip():
                raise ValidationError("All tags must be non-empty strings")


class SiteResponseSchema(Schema):
    """Schema para serializar la respuesta de un sitio histórico"""

    id = fields.Int()
    name = fields.Str()
    short_description = fields.Str()
    description = fields.Str()
    city = fields.Str()
    province = fields.Str()
    country = fields.Str()
    lat = fields.Float()
    long = fields.Float()
    tags = fields.List(fields.Str())
    state_of_conservation = fields.Str()
    inauguration_year = fields.Int()
    category = fields.Str(allow_none=True)
    inserted_at = fields.DateTime(format='iso', data_key='inserted_at')
    updated_at = fields.DateTime(format='iso', data_key='updated_at')
    user_id = fields.Int(dump_only=True)  # Solo en respuestas de creación


class SiteListResponseSchema(Schema):
    """Schema para la respuesta paginada de sitios"""

    data = fields.List(fields.Nested(SiteResponseSchema))
    meta = fields.Dict()


def format_validation_errors(errors):
    """
    Formatea los errores de validación de Marshmallow al formato del PDF

    Args:
        errors: Dict de errores de Marshmallow

    Returns:
        Dict con formato {"error": {"code": "...", "message": "...", "details": {...}}}
    """
    details = {}

    for field, messages in errors.items():
        if isinstance(messages, list):
            details[field] = messages
        elif isinstance(messages, dict):
            # Para errores anidados
            details[field] = [str(messages)]
        else:
            details[field] = [str(messages)]

    return {
        "error": {
            "code": "invalid_data",
            "message": "Invalid input data",
            "details": details
        }
    }