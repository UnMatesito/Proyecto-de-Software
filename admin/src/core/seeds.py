from core.database import db
from core.models import Issue, User, Label
from core.services.issue_service import assign_labels


def run():
    user1 = User(email="usuario1@ejemplo.com", username="UsuarioUno", password_hash="password1")
    user2 = User(email="usuario2@ejemplo.com", username="UsuarioDos", password_hash="password2")
    user3 = User(email="usuario3@ejemplo.com", username="UsuarioTres", password_hash="password3")
    db.session.add_all([user1, user2, user3])
    db.session.commit()

    issue1 = Issue(user_id=user1.id, email=user1.email, title="Error en login",
                   description="No se puede iniciar sesión", status="Abierto")
    issue2 = Issue(user_id=user2.id, email=user2.email, title="Página no encontrada",
                   description="El enlace lleva a un 404", status="En progreso")
    issue3 = Issue(user_id=user3.id, email=user3.email, title="Mejora de rendimiento", description="Carga lenta",
                   status="Cerrado")
    db.session.add_all([issue1, issue2, issue3])

    label1 = Label(name="bug")
    label2 = Label(name="enhancement")
    label3 = Label(name="urgent")
    db.session.add_all([label1, label2, label3])

    assign_labels(issue1, [label1, label2])
    assign_labels(issue2, [label1])
    assign_labels(issue3, [label3])

    db.session.commit()
