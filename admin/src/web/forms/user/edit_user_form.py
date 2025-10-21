from flask_wtf import FlaskForm
from wtforms import BooleanField, EmailField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length

from core.services import get_all_roles


class EditUserForm(FlaskForm):
    """Form para editar un usuario"""

    first_name = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El nombre es obligatorio"),
            Length(max=50, message="El maximo es de 50 caracteres"),
        ],
    )

    last_name = StringField(
        "Apellido",
        validators=[
            DataRequired(message="El apellido es obligatorio"),
            Length(max=50, message="El maximo es de 50 caracteres"),
        ],
    )

    email = EmailField(
        "Correo",
        validators=[
            DataRequired(message="El correo es obligatorio"),
            Email(message="Ingrese un correo valido"),
            Length(max=120, message="El maximo es de 120 caracteres"),
        ],
    )

    submit = SubmitField("Editar usuario")
