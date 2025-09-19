from core.database import db
from core.models import Issue, User


def run():
    # Usuarios de ejemplo
    user1 = User(
        email="usuario1@ejemplo.com", username="UsuarioUno", password_hash="password1"
    )
    user2 = User(
        email="usuario2@ejemplo.com", username="UsuarioDos", password_hash="password2"
    )
    user3 = User(
        email="usuario3@ejemplo.com", username="UsuarioTres", password_hash="password3"
    )
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)

    # Issues de ejemplo
    issue1 = Issue(
        email="usuario1@ejemplo.com",
        title="Error en login",
        description="No se puede iniciar sesión con credenciales válidas",
        status="Abierto",
    )
    issue2 = Issue(
        email="usuario2@ejemplo.com",
        title="Página no encontrada",
        description="El enlace a la documentación lleva a un 404",
        status="En progreso",
    )
    issue3 = Issue(
        email="usuario3@ejemplo.com",
        title="Mejora de rendimiento",
        description="La carga de la página principal es lenta",
        status="Cerrado",
    )
    db.session.add(issue1)
    db.session.add(issue2)
    db.session.add(issue3)

    db.session.commit()
