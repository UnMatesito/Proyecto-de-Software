from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField


class BlockUserForm(FlaskForm):
    block = BooleanField("Bloquear usuario")
    submit = SubmitField("Confirmar cambios")
