from flask_wtf import FlaskForm
from wtforms import SubmitField


class DeleteTagForm(FlaskForm):
    submit = SubmitField("Eliminar")
