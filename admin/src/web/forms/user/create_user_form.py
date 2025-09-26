from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from core.services import get_all_roles

class CreateUserForm(FlaskForm):
    """Formulario con wtforms para la carga de un usuario"""
    first_name = StringField("Nombre", 
        validators=[DataRequired(message= "El nombre es obligatorio"),
                    Length(max=50, message="El maximo es de 50 caracteres")
                    ])
    
    last_name = StringField("Apellido",
        validators=[DataRequired(message="El apellido es obligatorio"),
                    Length(max=50, message="El maximo es de 50 caracteres")
                    ])
    
    email = StringField("Correo",
        validators=[DataRequired(message="El correo es obligatorio"),
                    Email(message="Ingrese un correo valido"),
                    Length(max=120, message="El maximo es de 120 caracteres")
                    ])
    
    password = PasswordField("Contraseña", 
        validators=[DataRequired(message="La contraseña es obligatorio"),
                    Length(min=6, message="Minimo 6 caracteres")
                    ])
    
    confirm_password = PasswordField ("Confirmar Contraseña",
        validators=[DataRequired(message="Confirme la contraseña"),
                    EqualTo("password", message= "Las contraseñas no coinciden")
                    ])
    
    role_id = SelectField("Rol",
        coerce=int,
        validators=[ DataRequired(message="Seleccione un rol")
                    ])
    
    system_admin = BooleanField("Administrador del sistema")

    submit = SubmitField("Crear usuario")

    def __init__(self, *args, **kwargs):
        """Constructor"""
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.role_id.choices = [(0, "Seleccionar rol ")]+[      #Cargo los roles en el select 
            (role.id, role.name) for role in get_all_roles()    
        ]
    


    

    