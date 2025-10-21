from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class EditTagForm(FlaskForm):
    name = StringField(
        "Ingresa el nuevo nombre del tag",
        validators=[
            DataRequired(message="El nombre del tag es obligatorio"),
            Length(
                min=3, max=50, message="La cantidad de caracteres debe ser entre 3 y 50"
            ),
        ],
    )
    submit = SubmitField("Editar")
