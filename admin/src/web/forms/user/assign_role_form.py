from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired

from core.services import role_service


class AssignRoleForm(FlaskForm):
    role_id = SelectField(
        "Rol",
        coerce=int,
        validators=[DataRequired(message="Debe seleccionar un rol")],
        choices=[],
    )
    submit = SubmitField("Asignar Rol")

    def __init__(self, *args, **kwargs):
        super(AssignRoleForm, self).__init__(*args, **kwargs)
        # Cargar roles disponibles
        roles = role_service.get_all_roles()
        self.role_id.choices = [(role.id, role.name) for role in roles]
