from datetime import datetime, timezone

from flask_wtf import FlaskForm
from wtforms import (
    FloatField,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Length, NumberRange

from core.services import (
    get_all_categories,
    get_all_conservation_state,
    get_all_not_deleted_tags,
    get_all_provinces,
)


class CreateSiteForm(FlaskForm):
    name = StringField(
        "Nombre del sitio",
        validators=[
            DataRequired(message="El nombre del sitio es obligatorio"),
        ],
    )

    brief_description = StringField(
        "Descripcion breve del sitio",
        validators=[
            DataRequired(message="La descripcion breve del sitio es obligatoria"),
        ],
    )

    full_description = StringField(
        "Descripcion completa del sitio",
        validators=[
            DataRequired(message="La descripcion completa del sitio es obligatoria"),
        ],
    )

    inauguration_year = IntegerField(
        "Año de inaguracion del sitio",
        validators=[
            DataRequired(message="El año de inauguración del sitio es obligatorio"),
            NumberRange(
                min=1000,
                max=datetime.now(timezone.utc).year,
                message="La latitud se debe encontrar en un rago de -90 a 90",
            ),
        ],
    )

    province = SelectField(
        "Provincia",
        coerce=int,
        validators=[
            DataRequired(message="La provincia es obligatoria"),
        ],
    )

    city = SelectField(
        "Ciudad",
        coerce=int,
        choices=[],
        validators=[
            DataRequired(message="La ciudad es obligatoria"),
        ],
        validate_choice=False,
    )

    conservation_state = SelectField(
        "Estado de conservación",
        coerce=int,
        validators=[
            DataRequired(message="El estado de conservación es obligatorio"),
        ],
    )

    category = SelectField(
        "Categoria",
        coerce=int,
        validators=[
            DataRequired(message="La categoria es obligatoria"),
        ],
    )

    latitude = FloatField(
        "Latitud",
        render_kw={"readonly": True},
        validators=[
            DataRequired("La latitud es obligatoria"),
            NumberRange(
                min=-90,
                max=90,
                message="La latitud se debe encontrar en un rago de -90 a 90",
            ),
        ],
    )

    longitude = FloatField(
        "Longitud",
        render_kw={"readonly": True},
        validators=[
            DataRequired("La longitud es obligatoria"),
            NumberRange(
                min=-180,
                max=180,
                message="La latitud se debe encontrar en un rago de -180 a 180",
            ),
        ],
    )

    tags = SelectMultipleField(
        "Seleccionar Tags",
        coerce=int,
    )

    submit = SubmitField("Crear")

    def __init__(self, *args, **kwargs):
        """Constructor"""
        super(CreateSiteForm, self).__init__(*args, **kwargs)

        self.province.choices = [
            (0, "Seleccionar provincia ")
        ] + [  # Cargo las provincias en el select
            (province.id, province.name) for province in get_all_provinces()
        ]

        self.conservation_state.choices = [
            (0, "Seleccionar estado de conservación")
        ] + [  # Cargo los estados en el select
            (state.id, state.state) for state in get_all_conservation_state()
        ]

        self.category.choices = [
            (0, "Seleccionar category")
        ] + [  # Cargo las categorias en el select
            (category.id, category.name) for category in get_all_categories()
        ]

        self.tags.choices = [  # Cargo las tags en el select
            (tag.id, tag.name) for tag in get_all_not_deleted_tags()
        ]
