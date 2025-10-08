from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired, Length 


class ToggleFeatureFlagForm(FlaskForm):
    """Form para los flags de mantenimiento, ingresar el mensaje """
    flag_id = HiddenField("Flag ID")
    message = StringField(
        "Mensaje de mantenimiento",
        validators=[
            DataRequired(message="El mensaje es obligatorio"),  
            Length(
                min=10, max=255, message="La cantidad de caracteres debe ser entre 10 y 255"
            ),
        ],
    )
    submit = SubmitField("Guardar cambios")
