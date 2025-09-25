from flask import Blueprint, render_template, request, redirect, url_for, flash

from core.utils.auth import login_required, permission_required
from web.forms.user import AssignRoleForm, CreateUserForm ## ChangePasswordForm, EditUserForm

from core.services.user_service import (
    get_all_users,
    get_user_by_id,
    create_user,
    update_user_attribute,
    delete_user,
    block_user,
    unblock_user,
    change_password,
    assign_role,
    restore_user
)

user_bp = Blueprint('users', __name__, url_prefix='/users')

@user_bp.route("/")
def list_users():
    """Lista los usuarios y opciones """
    try:
        users = get_all_users()
        return render_template("users/index.html", users=users)
    except Exception as e:
        flash(f'Error al cargar usuarios: {str(e)}', 'error') #Envia un  mensaje temporal a la sesión
        return render_template("users/index.html", users=[] )

@user_bp.route("/create", methods= ["GET", "POST"])
def create():
    """Crear un nuevo usuario"""
    form = CreateUserForm()
    if form.validate_on_submit():  #Valida los datos del formulario y comprueba si la solicitud es un POST , caso contrario renderizo el template 
        try:
            user_data = {
                "first_name": form.first_name.data,
                "last_name": form.last_name.data,
                "email": form.email.data,
                "password": form.password.data,
                "role_id": form.role_id.data,
                "system_admin": form.system_admin.data
            }
            user = create_user(**user_data)
            user = create_user(**user_data)
            flash(f'Usuario {user.get_full_name()} creado exitosamente', 'success')
            return redirect(url_for('users.index'))
        except ValueError as e:
            flash(str(e), 'error')
        except RuntimeError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error inesperado: {str(e)}', 'error')

    return render_template('users/create.html', form=form)

@user_bp.route("/<int:user_id>/delete", methods= ["POST"])
def delete_user_rute(user_id):
    """Borrar un usuario """
    try:
        delete_user(user_id)
        flash("Usuario eliminado","success")
    except ValueError as e:
        flash(str(e), 'warning')
    except RuntimeError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error inesperado: {str(e)}', 'error')

    return redirect(url_for("users.list_users"))

@user_bp.route("/<int:user_id>/restore", methods= ["POST"])
def restore_user_rute(user_id):
    """Recuperar un usuario """
    try:
        restore_user(user_id)
        flash("Usuario recuperado","success")
    except ValueError as e:
        flash(str(e), 'warning')
    except RuntimeError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error inesperado: {str(e)}', 'error')

    return redirect(url_for("users.list_users"))

