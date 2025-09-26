from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length
from core.services import get_all_roles

class ChangePasswordForm(FlaskForm):
    """Formulario para cambio de contraseña"""
    old_password = PasswordField("Contraseña antigua", 
        validators=[DataRequired(message="La contraseña es obligatoria"),
                    Length(min=6, message="Minimo 6 caracteres")
                    ])
    new_password = PasswordField("Contraseña nueva", 
        validators=[DataRequired(message="La contraseña es obligatorio"),
                    Length(min=6, message="Minimo 6 caracteres")
                    ])
    confirm_password = PasswordField ("Confirmar Contraseña",
        validators=[DataRequired(message="Confirme la contraseña"),
                    EqualTo("new_password", message= "Las contraseñas no coinciden")
                    ])
    
    submit = SubmitField('Cambiar Contraseña')