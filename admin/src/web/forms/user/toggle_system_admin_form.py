from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField
from wtforms.validators import Optional

class ToggleSystemAdminForm(FlaskForm):
    system_admin = BooleanField("System Admin", validators=[Optional()])
    submit = SubmitField("Actualizar")
