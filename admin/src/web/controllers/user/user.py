from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from core.services.role_service import get_all_roles
from core.services.user_service import (
    assign_role,
    change_password,
    change_password_by_admin,
    create_user,
    delete_user,
    get_paginated_users,
    get_user_by_email,
    get_user_by_id,
    restore_user,
    update_user_attribute,
)
from web.forms.user import (
    ChangePasswordByAdminForm,
    ChangePasswordForm,
    CreateUserForm,
    EditUserForm,
)
from web.utils.auth import get_user_role_name, login_required, permission_required

user_bp = Blueprint("users", __name__, url_prefix="/users")


@user_bp.get("/")
@login_required
@permission_required("user_index")
def index():
    """Lista los usuarios y opciones"""
    try:
        order_by = request.args.get("order_by", "name")
        sorted_by = request.args.get("sorted_by", "asc")
        page = request.args.get("page", 1)
        blocked_param = request.args.get("blocked", None)
        role_id = request.args.get("role_id", None)
        email = request.args.get("email", None)
        columns = [
            {"key": "id", "label": "ID"},
            {"key": "full_name", "label": "Usuario", "render": "user_name"},
            {"key": "email", "label": "Correo"},
            {
                "key": "role",
                "label": "Rol",
                "render": lambda user: get_user_role_name(user.id) or "Sin rol",
            },
            {"key": "status", "label": "Estado", "render": "status"},
            {"key": "created_at", "label": "Creado", "render": "date"},
        ]
        users_page = get_paginated_users(
            page=page,
            order_by=order_by,
            sorted_by=sorted_by,
            blocked=blocked_param,
            role_id=role_id,
            email=email
        )
        roles = get_all_roles()
        return render_template(
            "users/index.html",
            pagination=users_page,
            columns=columns,
            roles=roles,
            blocked=blocked_param,
            role_id=role_id,
            sorted_by=sorted_by,
            order_by=order_by,
        )
    except Exception as e:
        flash(
            f"Error al cargar usuarios: {str(e)}", "error"
        )  # Envia un  mensaje temporal a la sesión
        return render_template("users/index.html", pagination=[], columns=[])


@user_bp.get("/<int:user_id>")
@login_required
@permission_required("user_show")
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


@user_bp.get("/search-by-mail")
@login_required
@permission_required("user_show")
def search_by_email():
    """Busca a un usuario por correo"""
    correo = request.args.get("email", "").strip()
    user = get_user_by_email(correo)
    if not user:
        return render_template("users/index.html", pagination=[], columns=[])
    
    return redirect(url_for("users.index",email=correo))


@user_bp.post("/create")
@login_required
@permission_required("user_new")
def create_post():
    """Crear un nuevo usuario"""
    current_user = get_user_by_id(session["user_id"])
    form = CreateUserForm()
    if form.validate_on_submit():
        try:
            user_data = {
                "first_name": form.first_name.data,
                "last_name": form.last_name.data,
                "email": form.email.data,
                "password": form.password.data,
                "role_id": form.role_id.data,
            }
            # Si por alguna razon quiere que el usuario sea system admin y el que hace la peticion no es system admin, lo carga False
            if current_user.is_admin():
                user_data["system_admin"] = form.system_admin.data
            else:
                user_data["system_admin"] = False

            user = create_user(**user_data)
            flash(f"Usuario {user.get_full_name()} creado exitosamente", "success")
            return redirect(url_for("users.index"))
        except ValueError as e:
            flash(str(e), "error")
        except RuntimeError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error inesperado: {str(e)}", "error")

    # Si no valida, vuelve a mostrar el formulario
    return render_template(
        "users/create.html", form=form, is_system_admin=current_user.is_admin()
    )


@user_bp.get("/create")
@login_required
@permission_required("user_new")
def create_get():
    """Mostrar el formulario para crear un nuevo usuario"""
    current_user = get_user_by_id(session["user_id"])
    form = CreateUserForm()
    return render_template(
        "users/create.html", form=form, is_system_admin=current_user.is_admin()
    )


@user_bp.get("/<int:user_id>/edit")
@login_required
@permission_required("user_update")
def edit_get(user_id):
    """Mostrar el formulario para editar un usuario"""
    current_user = get_user_by_id(session["user_id"])
    try:
        user = get_user_by_id(user_id)
        if not user:
            flash("Usuario no encontrado", "error")
            return redirect(url_for("users.index"))
        # Un admin no puede editar a un system admin
        if user.is_admin() and not current_user.is_admin():
            flash(
                "No puede modificar un System Admin si usted no es System Admin",
                "error",
            )
            return redirect(url_for("users.index"))

        form = EditUserForm(
            obj=user
        )  # Rellena los campos del form con los datos del usuario
        return render_template(
            "users/edit.html",
            form=form,
            user=user,
        )
    except Exception as e:
        flash(f"Error al editar el usuario: {str(e)}", "error")
        return redirect(url_for("users.index"))


@user_bp.post("/<int:user_id>/edit")
@login_required
@permission_required("user_update")
def edit_post(user_id):
    """Editar un usuario"""
    current_user = get_user_by_id(session["user_id"])
    try:
        user = get_user_by_id(user_id)
        if not user:
            flash("Usuario no encontrado", "error")
            return redirect(url_for("users.index"))
        # Un admin no puede editar a un system admin
        if user.is_admin() and not current_user.is_admin():
            flash(
                "No puede modificar un System Admin si usted no es System Admin",
                "error",
            )
            return redirect(url_for("users.index"))
        form = EditUserForm(obj=user)
        if form.validate_on_submit():
            # Actualizo los atributos
            update_user_attribute(user_id, "first_name", form.first_name.data)
            update_user_attribute(user_id, "last_name", form.last_name.data)
            update_user_attribute(user_id, "email", form.email.data)

            # Si cambia el rol lo actualizo
            if user.role_id != form.role_id.data:
                assign_role(user_id, form.role_id.data)

            flash("Usuario actualizado correctamente", "success")
            return redirect(url_for("users.detail", user_id=user_id))

        # Si no valida, vuelvo a mostrar el form
        return render_template(
            "users/edit.html",
            form=form,
            user=user,
            is_system_admin=current_user.is_admin(),
        )
    except Exception as e:
        flash(f"Error al editar el usuario: {str(e)}", "error")
        return redirect(url_for("users.index"))


@user_bp.post("/<int:user_id>/delete")
@login_required
@permission_required("user_destroy")
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


@user_bp.post("/<int:user_id>/restore")
@login_required
@permission_required("user_update")
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


@user_bp.post("/<int:user_id>/change-password")
@login_required
@permission_required("user_update")
def change_password_post(user_id):
    """Procesar el cambio de contraseña"""
    current_user = get_user_by_id(session["user_id"])
    try:
        user = get_user_by_id(user_id)
        if not user:
            flash("Usuario no encontrado", "error")
            return redirect(url_for("users.index"))
        
        if user.is_admin() and not current_user.is_admin():
            flash(
                "No puede cambiar la contraseña de un administrador del sistema si usted no es administrador del sistema",
                "error",
            )
            return redirect(url_for("users.index"))

        if user.has_role("Administrador") and not current_user.is_admin():
            flash(
                "No puede cambiar la contraseña de un administrador si usted no es administrador del sistema",
                "error",
            )
            return redirect(url_for("users.index"))

        form = ChangePasswordByAdminForm()
        if form.validate_on_submit():
            try:
                change_password_by_admin(user_id, form.new_password.data)
                flash("Contraseña actualizada", "success")
                return redirect(url_for("users.detail", user_id=user_id))
            except ValueError as e:
                flash(str(e), "warning")
            except Exception as e:
                flash(f"Error al cambiar contraseña: {str(e)}", "error")
        # Si el form no valida, se muestra de nuevo
        return render_template(
            "users/change_password_by_admin.html", form=form, user=user
        )
    except Exception as e:
        flash(f"Error inesperado: {str(e)}", "error")
        return redirect(url_for("users.index"))


@user_bp.get("/<int:user_id>/change-password")
@login_required
@permission_required("user_update")
def change_password_get(user_id):
    """Mostrar el formulario para cambiar la contraseña"""
    current_user = get_user_by_id(session["user_id"])
    try:
        user = get_user_by_id(user_id)
        if not user:
            flash("Usuario no encontrado", "error")
            return redirect(url_for("users.index"))
        
        if user.is_admin() and not current_user.is_admin():
            flash(
                "No puede cambiar la contraseña de un administrador del sistema si usted no es administrador del sistema",
                "error",
            )
            return redirect(url_for("users.index"))

        if user.has_role("Administrador") and not current_user.is_admin():
            flash(
                "No puede cambiar la contraseña de un administrador si usted no es administrador del sistema",
                "error",
            )
            return redirect(url_for("users.index"))

        form = ChangePasswordByAdminForm()
        return render_template(
            "users/change_password_by_admin.html", form=form, user=user
        )
    except Exception as e:
        flash(f"Error inesperado: {str(e)}", "error")
        return redirect(url_for("users.index"))


@user_bp.get("/change-password")
@login_required
def change_self_password_get():
    """Mostrar el formulario para cambiar la contraseña del usuario que realizo la peticion"""
    current_user = get_user_by_id(session["user_id"])
    try:
        if not current_user:
            flash("Usuario no encontrado", "error")
            return redirect(url_for("main_bp.home"))
        form = ChangePasswordForm()
        return render_template(
            "users/change_password.html", form=form, user=current_user
        )
    except Exception as e:
        flash(f"Error inesperado: {str(e)}", "error")
        return redirect(url_for("main_bp.home"))  # Lo mando al home en caso de error


@user_bp.post("/change-password")
@login_required
def change_self_password_post():
    """Procesar el cambio de contraseña del usuario que realizo la peticion"""
    try:
        current_user = get_user_by_id(session["user_id"])
        if not current_user:
            flash("Usuario no encontrado", "error")
            return redirect(url_for("main_bp.home"))

        form = ChangePasswordForm()
        if form.validate_on_submit():
            try:
                change_password(
                    session["user_id"], form.old_password.data, form.new_password.data
                )
                flash("Contraseña actualizada", "success")
                return redirect(url_for("users.detail", user_id=session["user_id"]))
            except ValueError as e:
                flash(str(e), "warning")
            except Exception as e:
                flash(f"Error al cambiar contraseña: {str(e)}", "error")
        # Si el form no valida, se muestra de nuevo
        return render_template(
            "users/change_password.html", form=form, user=current_user
        )
    except Exception as e:
        flash(f"Error inesperado: {str(e)}", "error")
        return redirect(url_for("main_bp.home"))  # Lo mando al home en caso de error
