from core.models import User
from admin.src.web import create_app

app = create_app()
app.app_context().push()


# Obtener todos los usuarios
user = User.query.all()
print(user)
# Obtener un usuario por su ID
user = User.query.filter(User.id=="1").first()
print(user)
# Obtener un usuario por su email
user = User.query.filter_by(email="admin@sistema.com").first()
print(user)