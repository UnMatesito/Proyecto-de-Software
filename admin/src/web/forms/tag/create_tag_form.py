from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class CreateTagForm(FlaskForm):
    name = StringField(
        "Ingresa el nombre del tag que deseas crear",
        validators=[
            DataRequired(message="El nombre del tag es obligatorio"),
            Length(
                min=3, max=50, message="La cantidad de caracteres debe ser entre 3 y 50"
            ),
        ],
    )
    submit = SubmitField("Crear")
