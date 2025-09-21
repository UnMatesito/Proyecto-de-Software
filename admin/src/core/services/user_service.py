from core.database import db
from core.models import User

# from core.models import Role


def list_users():
    return User.query.all()


def get_user_by_id(user_id):
    return User.query.get(user_id)


# Falta hacer el hash de la passw
def create_user(**kwargs):
    user = User(**kwargs)
    db.session.add(user)
    db.session.commit()
    return user


"""
Cuando cree los serv de deleted y block, me di cuenta que es casi el mismo codigo, entonces lo reciclo en esta funcion que hace un update de x atributo 
Le llega user_id para checkear que exista el user, el atributo a modificar, el valor, y la funcion que verifica el estado del atributo 
"""


def update_user_attribute(user_id, attr_name, new_value, check_func=None):
    # Checkeo si existe el usuario
    user = User.query.get(user_id)
    if not user:
        raise ValueError(f"No existe el usuario con id {user_id}")
    if check_func:
        msg = check_func(user)
        if msg:
            raise ValueError(msg)
    """
    hasattr permite asignar dinámicamente un valor a un atributo de un objeto
     setattr(objeto, "nombre_del_atributo", valor), pero tengo que checkear que exista dicho atributo de lo contrario creara una nuevo 
    """
    if hasattr(user, attr_name):
        setattr(user, attr_name, new_value)
    else:
        raise AttributeError(f"{attr_name} no es un atributo de User")
    # Intento actualizar la db
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error al eliminar el usuario: {e}")
    return True


# Borra un usuario
def delete_user(user_id):
    # Funcion para checkear que si el usuario esta borrado, se manda como parametro
    def check_delete(user):
        if user.deleted_at is not None:
            return f"El usuario {user.name} ya esta eliminado"
        return None

    return update_user_attribute(
        user_id, "deleted_at", datetime.now(timezone.utc), check_delete
    )


# Bloquea un usuario
def block_user(user_id):
    # Funcion para checkear que si el usuario esta bloqueado, se manda como parametro
    def check_blocked(user):
        if user.blocked:
            return f"El usuario {user.name} ya esta bloqueado"
        return None

    return update_user_attribute(user_id, "blocked", True, check_blocked)


# Desbloquea un usuario
def block_user(user_id):
    # Funcion para checkear que si el usuario esta desbloqueado, se manda como parametro
    def check_blocked(user):
        if not user.blocked:
            return f"El usuario {user.name} ya esta desbloqueado"
        return None

    return update_user_attribute(user_id, "blocked", False, check_blocked)


# Asigna un rol
"""
def assign_role(user_id, role_id):
    role= Role.query.get(role_id)
    if not role:
        raise ValueError(f"No existe el rol con id {role_id}")
    def role_check(user):
        if user.role_id == role_id:
            return f"El usuario {user.name} ya tiene dicho rol"
        return None
    return update_user_attribute(user_id, "role_id", role_id, role_check)
"""
