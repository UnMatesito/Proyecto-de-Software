from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class ToggleFeatureFlagForm(FlaskForm):
    flag_id = HiddenField("Flag ID")
    message = StringField(
        "Mensaje de mantenimiento",
        validators=[
            Optional(),  # Solo es obligatorio si el flag es de mantenimiento y se activa
            Length(max=10, message="El mensaje no puede superar los 255 caracteres"),
        ],
    )
    submit = SubmitField("Guardar cambios")
