from flask import Blueprint, flash, redirect, render_template, request, url_for

from core.services.role_service import get_all_roles
from core.services.user_service import (
    assign_role,
    change_password,
    create_user,
    delete_user,
    get_all_users,
    get_paginated_users,
    get_user_by_email,
    get_user_by_id,
    restore_user,
    update_user_attribute,
)
from web.forms.user import ChangePasswordForm, CreateUserForm, EditUserForm
from web.utils.auth import login_required, permission_required

user_bp = Blueprint("users", __name__, url_prefix="/users")


# @login_required
# @permission_required("user_index")
@user_bp.route("/")
def index():
    """Lista los usuarios y opciones"""
    try:
        order_by = request.args.get("order_by", "name")
        sorted_by = request.args.get("sorted_by", "asc")
        page = request.args.get("page", 1)
        active_param = request.args.get("active", None)
        role_id = request.args.get("role_id", None)
        users_page = get_paginated_users(
            page=page,
            order_by=order_by,
            sorted_by=sorted_by,
            active=active_param,
            role_id=role_id,
        )
        roles = get_all_roles()
        return render_template(
            "users/index.html",
            pagination=users_page,
            roles=roles,
            active=active_param,
            role_id=role_id,
            sorted_by=sorted_by,
            order_by=order_by,
        )
    except Exception as e:
        flash(
            f"Error al cargar usuarios: {str(e)}", "error"
        )  # Envia un  mensaje temporal a la sesión
        return render_template(
            "users/index.html",
            pagination={"items": [], "has_prev": False, "has_next": False, "page": 1, "pages": 0, "total": 0},
            roles=[],
            active=None,
            role_id=None,
            sorted_by="asc",
            order_by="created_at"
        )


# @login_required
# @permission_required("user_show")
@user_bp.route("/<int:user_id>")
def detail(user_id):
    """Informacion de un usuario"""
    try:
        user = get_user_by_id(user_id)
        if not user:
            flash("Usuario no encontrado", "error")
            return redirect(url_for("users.index"))
        return render_template("users/detail.html", user=user)
    except Exception as e:
        flash(f"Error al cargar el usuario: {str(e)}", "error")
        return redirect(url_for("users.index"))


# @login_required
# @permission_required("user_show")
@user_bp.route("/search-by-mail")
def search_by_email():
    correo = request.args.get("email", "").strip()
    user = get_user_by_email(correo)
    users = [user] if user else get_all_users()

    return render_template("users/index.html", users=users)


# @login_required
# @permission_required("user_new")
@user_bp.route("/create", methods=["GET", "POST"])
def create():
    """Crear un nuevo usuario"""
    form = CreateUserForm()
    if (
        form.validate_on_submit()
    ):  # Valida los datos del formulario y comprueba si la solicitud es un POST , caso contrario renderizo el template
        try:
            user_data = {
                "first_name": form.first_name.data,
                "last_name": form.last_name.data,
                "email": form.email.data,
                "password": form.password.data,
                "role_id": form.role_id.data,
                "system_admin": form.system_admin.data,
            }
            user = create_user(**user_data)
            flash(f"Usuario {user.get_full_name()} creado exitosamente", "success")
            return redirect(url_for("users.index"))
        except ValueError as e:
            flash(str(e), "error")
        except RuntimeError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error inesperado: {str(e)}", "error")

    return render_template("users/create.html", form=form)


# @login_required
# @permission_required("user_update")
@user_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
def edit(user_id):
    """Editar un usuario"""
    try:
        user = get_user_by_id(user_id)
        if not user:
            flash("Usuario no encontrado", "error")
            return redirect(url_for("users.index"))

        form = EditUserForm(
            obj=user
        )  # Rellena los campos del form con los datos del usuario

        if form.validate_on_submit():
            # Actualizo los atributos
            update_user_attribute(user_id, "first_name", form.first_name.data)
            update_user_attribute(user_id, "last_name", form.last_name.data)
            update_user_attribute(user_id, "email", form.email.data)
            update_user_attribute(user_id, "active", form.active.data)
            update_user_attribute(user_id, "system_admin", form.system_admin.data)

            # Si cambia el rol lo actualizo
            if user.role_id != form.role_id.data:
                assign_role(user_id, form.role_id.data)
            flash("Usuario actualizado correctamente", "success")

            return redirect(url_for("users.details", user=user))
        return render_template("users/edit.html", form=form, user=user)

    except Exception as e:
        flash(f"Error al editar el usuario: {str(e)}", "error")
        return redirect(url_for("users.index"))


# @login_required
# @permission_required("user_destroy")
@user_bp.route("/<int:user_id>/delete", methods=["POST"])
def delete(user_id):
    """Borrar un usuario"""
    try:
        delete_user(user_id)
        flash("Usuario eliminado", "success")
    except ValueError as e:
        flash(str(e), "warning")
    except RuntimeError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Error inesperado: {str(e)}", "error")

    return redirect(url_for("users.index"))


# @login_required
# @permission_required("user_update")
@user_bp.route("/<int:user_id>/restore", methods=["POST"])
def restore(user_id):
    """Recuperar un usuario"""
    try:
        restore_user(user_id)
        flash("Usuario recuperado", "success")
    except ValueError as e:
        flash(str(e), "warning")
    except RuntimeError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Error inesperado: {str(e)}", "error")

    return redirect(url_for("users.index"))


# @login_required
# @permission_required("user_update")
@user_bp.route("/<int:user_id>/change-password", methods=["GET", "POST"])
def change_password(user_id):
    """Cambiar la contraseña de un usuario"""
    try:
        user = get_user_by_id(user_id)
        if not user:
            flash("Usuario no encontrado", "error")
            return redirect(url_for("users.index"))

        form = ChangePasswordForm()

        if form.validate_on_submit():
            try:
                change_password(user_id, form.old_password.data, form.new_password.data)
                flash("Contraseña actualizada", "success")
                return redirect(url_for("users.detail", user=user))
            except ValueError as e:
                flash(str(e), "warning")
            except Exception as e:
                flash(f"Error al cambiar contraseña: {str(e)}", "error")
        return render_template("users/change_password.html", form=form, user=user)

    except Exception as e:
        flash(f"Error inesperado: {str(e)}", "error")
        return redirect(url_for("users.list_users"))
