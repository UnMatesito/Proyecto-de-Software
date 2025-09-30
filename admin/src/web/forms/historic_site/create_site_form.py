from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from core.services import get_all_conservation_state, get_all_categories, get_all_provinces

class CreateSiteForm(FlaskForm):
    name = StringField(
        "Nombre del sitio",
        validators=[
            DataRequired(message="El nombre del site es obligatorio"),
        ]
    )

    brief_description = StringField(
        "Descripcion brebe del sitio",
        validators=[
            DataRequired(message="El descripcion brebe del site es obligatoria"),
        ]
    )

    full_description = StringField(
        "Descripcion completa del sitio",
        validators=[
            DataRequired(message="La descripcion completa del site es obligatoria"),
        ]
    )

    inauguration_year = StringField(
        "Año de inaguracion del sitio",
        validators=[
            DataRequired(message="El año de inaguracion del site es obligatorio"),
        ]
    )
    
    province =  SelectField(
        "Provincia",
        coerce=int,
        validators=[
            DataRequired(message="La provincia es obligatoria"),
        ]    
    )

    city =  SelectField(
        "Ciudad",
        coerce=int,
        choices=[],
        validators=[
            DataRequired(message="La ciudad es obligatoria"),
        ],
        validate_choice=False
    )

    conservation_state = SelectField(
        "Estado de conservacion",
        coerce=int,
        validators=[
            DataRequired(message="El estado de conservacion es obligatorio"),
        ]    
    )

    category = SelectField(
        "Categoria",
        coerce=int,
        validators=[
            DataRequired(message="La categoria es obligatoria"),
        ]    
    )

    submit = SubmitField("Crear")


    def __init__(self, *args, **kwargs):
        """Constructor"""
        super(CreateSiteForm, self).__init__(*args, **kwargs)
        self.province.choices = [
            (0, "Seleccionar provincia")
        ] + [  # Cargo las provincias en el select
            (province.id, province.name) for province in get_all_provinces()
        ]
        self.conservation_state.choices = [
            (0, "Seleccionar estado de conservacion ")
        ] + [  # Cargo los estados en el select
            (state.id, state.state) for state in get_all_conservation_state()
        ]
        self.category.choices = [
            (0, "Seleccionar categoria de conservacion ")
        ] + [  # Cargo las categortias en el select
            (category.id, category.name) for category in get_all_categories()
        ]