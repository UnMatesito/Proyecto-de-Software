from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from core.services import get_all_roles


class EditUserForm(FlaskForm):
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

    email = StringField(
        "Correo",
        validators=[
            DataRequired(message="El correo es obligatorio"),
            Email(message="Ingrese un correo valido"),
            Length(max=120, message="El maximo es de 120 caracteres"),
        ],
    )

    role_id = SelectField(
        "Rol",
        choices=[],
        coerce=int,
        validators=[DataRequired(message="El rol es obligatorio")],
    )

    system_admin = BooleanField("Administrador del sistema")

    active = BooleanField("Usuario activo")

    submit = SubmitField("Crear usuario")

    def __init__(self, *args, **kwargs):
        """Constructor"""
        super(EditUserForm, self).__init__(*args, **kwargs)
        # Cargar roles dinámicamente
        self.role_id.choices = [  # Cargo los roles en el select
            (role.id, role.name) for role in get_all_roles()
        ]
