"""
Schemas de validación para la API de Sitios Históricos usando Marshmallow
"""
from datetime import datetime, timezone

from marshmallow import (
    Schema,
    ValidationError,
    fields,
    validate,
    validates,
    validates_schema,
)

from core.services import conservation_state_service


class SiteQuerySchema(Schema):
    """Schema para validar parámetros de query en GET /sites"""

    name = fields.Str()
    description = fields.Str()
    city = fields.Str()
    province = fields.Str()
    tags = fields.Str()  # Separados por comas
    order_by = fields.Str(
        validate=validate.OneOf(["latest", "oldest", "rating-5-1", "rating-1-5"]),
        load_default="latest"
    )
    favorites = fields.Bool(load_default=False)
    lat = fields.Float(validate=validate.Range(min=-90, max=90))
    lon = fields.Float(validate=validate.Range(min=-180, max=180))
    radius = fields.Float(validate=validate.Range(min=0))
    page = fields.Int(validate=validate.Range(min=1), load_default=1)
    per_page = fields.Int(validate=validate.Range(min=1, max=100), load_default=20)

    @validates_schema
    def validate_geospatial(self, data, **kwargs):
        """Valida que si se usa búsqueda geoespacial, todos los parámetros estén presentes"""
        geo_fields = ['lat', 'lon', 'radius']
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
        validate=validate.Length(min=1),
        error_messages={"required": "This field is required"}
    )
    province = fields.Str(
        required=True,
        validate=validate.Length(min=1),
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
    lon = fields.Float(
        required=True,
        validate=validate.Range(min=-180, max=180),
        error_messages={
            "required": "This field is required",
            "invalid": "Must be a valid longitude between -180 and 180"
        }
    )
    tags = fields.List(
        fields.Str(validate=validate.Length(min=1)),
        required=True,
        validate=validate.Length(min=1),
        error_messages={"required": "This field is required"}
    )
    state_of_conservation = fields.Str(
        required=True,
        validate=validate.Length(min=1),
        error_messages={"required": "This field is required"}
    )
    inauguration_year = fields.Int(
        required=True,
        validate=validate.Range(min=1000, max=datetime.now(timezone.utc).year),
        error_messages={
            "required": "This field is required",
            "invalid": "Must be an integer between 1000 and the current year"
        }
    )
    category = fields.Str(allow_none=True, load_default=None)

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

    @validates('city')
    def validate_city(self, value):
        """Valida que la ciudad exista (se valida junto con provincia en validates_schema)"""

        # Solo validamos que no esté vacío, la existencia se valida en validates_schema
        if not value or not value.strip():
            raise ValidationError("City name cannot be empty")

    @validates('province')
    def validate_province(self, value):
        """Valida que la provincia exista"""
        from core.database import db
        from core.models import Province

        if not value or not value.strip():
            raise ValidationError("Province name cannot be empty")

        province = Province.query.filter(
            db.func.lower(Province.name) == value.lower()
        ).first()

        if not province:
            raise ValidationError(f"Province '{value}' does not exist")

    @validates_schema
    def validate_city_in_province(self, data, **kwargs):
        """Valida que la ciudad exista en la provincia especificada"""
        from core.database import db
        from core.models import City, Province

        city_name = data.get('city')
        province_name = data.get('province')

        if not city_name or not province_name:
            return  # Ya se validaron individualmente

        # Buscar provincia
        province = Province.query.filter(
            db.func.lower(Province.name) == province_name.lower()
        ).first()

        if not province:
            return  # Ya se validó en validate_province

        # Buscar ciudad en esa provincia
        city = City.query.filter(
            db.func.lower(City.name) == city_name.lower(),
            City.province_id == province.id
        ).first()

        if not city:
            raise ValidationError(
                f"City '{city_name}' does not exist in province '{province_name}'",
                field_name='city'
            )

    @validates('tags')
    def validate_tags(self, value):
        """Valida que tags sea una lista no vacía"""
        if not isinstance(value, list):
            raise ValidationError("Must be an array")
        if len(value) == 0:
            raise ValidationError("At least one tag is required")
        for tag in value:
            if not isinstance(tag, str) or not tag.strip():
                raise ValidationError("All tags must be non-empty strings")

class SiteImageSchema(Schema):
    """Schema para serializar imágenes de un sitio histórico"""

    id = fields.Int()
    url = fields.Str()
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1,max=100),
        error_messages={"required": "Image title is required"}
    )
    description = fields.Str(allow_none=True, validate=validate.Length(max=255))
    is_cover = fields.Bool()
    order = fields.Int()

class SiteResponseSchema(Schema):
    """Schema para serializar la respuesta de un sitio histórico"""

    id = fields.Int()
    name = fields.Str()
    short_description = fields.Str()
    description = fields.Str()
    review_count = fields.Int()
    average_rating = fields.Float()
    city = fields.Str()
    province = fields.Str()
    lat = fields.Float()
    lon = fields.Float()
    tags = fields.List(fields.Str())
    state_of_conservation = fields.Str()
    inauguration_year = fields.Int()
    category = fields.Str(allow_none=True)
    inserted_at = fields.DateTime(format='iso')
    updated_at = fields.DateTime(format='iso')
    images = fields.List(fields.Nested(SiteImageSchema))
    user_id = fields.Int(dump_only=True)

class SiteMetaSchema(Schema):
    """Schema para los metadatos de paginación"""

    page = fields.Int()
    per_page = fields.Int()
    total = fields.Int()
    total_pages = fields.Int()

class SiteListResponseSchema(Schema):
    """Schema para la respuesta paginada de sitios"""

    data = fields.List(fields.Nested(SiteResponseSchema))
    meta = fields.Nested(SiteMetaSchema)

class HistoricSiteShortSchema(Schema):
    """Schema corto para representar un sitio histórico dentro de otra entidad."""
    id = fields.Int()
    name = fields.Str()