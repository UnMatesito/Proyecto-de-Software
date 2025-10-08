from flask import Blueprint, flash, redirect, render_template, request, url_for

from core.services import role_service, user_service
from web.forms.user import AssignRoleForm, BlockUserForm, ToggleSystemAdminForm
from web.utils.auth import get_current_user, login_required, permission_required

user_management_bp = Blueprint("user_management", __name__)


@user_management_bp.get("/users/<int:user_id>/manage")
@login_required
@permission_required("user_show")
def manage_user(user_id):
    """
    Renderiza la página de gestión de un usuario específico.

    Args:
        user_id (int): ID del usuario a gestionar.

    Returns:
        Response: Página HTML con los formularios para asignar roles, bloquear o designar System Admin.

    Raises:
        Exception: Si ocurre un error al cargar los datos del usuario.
    """
    try:
        user = user_service.get_user_by_id(user_id)
        if not user:
            flash("Usuario no encontrado", "error")
            return redirect(url_for("users.index"))

        # Formularios
        assign_role_form = AssignRoleForm()
        block_form = BlockUserForm()
        toggle_system_admin_form = ToggleSystemAdminForm()

        # Precargar estado actual
        block_form.block.data = user.blocked
        toggle_system_admin_form.system_admin.data = user.system_admin

        return render_template(
            "users/manage.html",
            user=user,
            assign_role_form=assign_role_form,
            block_form=block_form,
            system_admin_form=toggle_system_admin_form,
        )

    except Exception as e:
        flash(f"Error al cargar la gestión del usuario: {str(e)}", "error")
        return redirect(url_for("users.index"))


@user_management_bp.post("/users/<int:user_id>/assign-role")
@login_required
@permission_required("user_update")
def assign_role(user_id):
    """
    Asigna un rol existente a un usuario.

    Args:
         user_id (int): ID del usuario al que se le asignará el rol.

    Returns:
        Response: Redirección a la vista de gestión del usuario.

    Raises:
        ValueError: Si el rol o el usuario no existen.
        Exception: Si ocurre un error general en la asignación.
    """
    form = AssignRoleForm()

    if form.validate_on_submit():
        try:
            # Verificar que el usuario existe
            user = user_service.get_user_by_id(user_id)
            if not user:
                flash("Usuario no encontrado", "error")
                return redirect(url_for("users.index"))

            # Verificar que el rol existe y es válido
            role = role_service.get_role_by_id(form.role_id.data)
            if not role:
                flash("Rol no válido", "error")
                return redirect(url_for("user_management.manage_user", user_id=user_id))

            current_user = get_current_user()
            if current_user and current_user.id == user.id:
                flash("No puede modificar su propio rol", "error")
                return redirect(url_for("user_management.manage_user", user_id=user_id))

            # Asignar el rol
            user_service.assign_role(user_id, form.role_id.data)
            flash(f'Rol "{role.name}" asignado exitosamente a {user.email}', "success")

        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error al asignar el rol: {str(e)}", "error")
    else:
        # Mostrar errores de validación
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error: {error}", "error")

    return redirect(url_for("user_management.manage_user", user_id=user_id))


@user_management_bp.post("/users/<int:user_id>/toggle-block")
@login_required
@permission_required("user_update")
def toggle_block(user_id):
    """
    Bloquea o desbloquea un usuario según el estado del formulario.

    Args:
        user_id (int): ID del usuario a bloquear o desbloquear.

    Returns:
        Response: Redirección a la vista de gestión del usuario.

    Raises:
        ValueError: Si el usuario no existe o no puede ser bloqueado.
        Exception: Si ocurre un error al modificar el estado.
    """
    form = BlockUserForm()

    if form.validate_on_submit():
        try:
            # Verificar que el usuario existe
            user = user_service.get_user_by_id(user_id)
            if not user:
                flash("Usuario no encontrado", "error")
                return redirect(url_for("users.index"))

            # Verificar que el usuario actual no se bloquee a sí mismo
            current_user = get_current_user()
            if current_user and current_user.id == user.id and form.block.data:
                flash("No puede bloquear su propia cuenta", "error")
                return redirect(url_for("user_management.manage_user", user_id=user_id))

            # Verificar que no es System Admin o Administrador si se intenta bloquear
            if form.block.data and user.system_admin:
                flash(
                    "No se puede bloquear a un usuario Administrador del sistema",
                    "error",
                )
                return redirect(url_for("user_management.manage_user", user_id=user_id))

            if form.block.data and user.has_role("Administrador"):
                flash(
                    "No se puede bloquear a un usuario con rol Administrador", "error"
                )
                return redirect(url_for("user_management.manage_user", user_id=user_id))

            # Bloquear o desbloquear
            if form.block.data:
                user_service.block_user(user_id)
                flash(f"Usuario {user.email} bloqueado exitosamente", "success")
            else:
                user_service.unblock_user(user_id)
                flash(f"Usuario {user.email} desbloqueado exitosamente", "success")

        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error al cambiar el estado del usuario: {str(e)}", "error")
    else:
        # Mostrar errores de validación
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error en {field}: {error}", "error")

    return redirect(url_for("user_management.manage_user", user_id=user_id))


@user_management_bp.post("/users/<int:user_id>/toggle-system-admin")
@login_required
@permission_required("user_update")
def toggle_system_admin(user_id):
    """
    Activa o desactiva el flag de System Admin de un usuario.

    Args:
        user_id (int): ID del usuario a modificar.

    Returns:
        Response: Redirección a la vista de gestión del usuario.

    Raises:
        ValueError: Si el usuario no tiene permisos suficientes o no existe.
        Exception: Si ocurre un error al actualizar el estado.
    """
    form = ToggleSystemAdminForm()

    if form.validate_on_submit():
        current_user = get_current_user()

        # Evitar que un usuario se quite su propio estado de System Admin
        if current_user and current_user.id == user_id:
            flash("No puede modificar su propio estado de Administrador del sistema", "error")
            return redirect(url_for("user_management.manage_user", user_id=user_id))

        # Solo un admin del sistema puede cambiar este valor
        if not current_user or not current_user.system_admin:
            flash("Solo un Administrador del sistema puede cambiar este valor", "error")
            return redirect(url_for("user_management.manage_user", user_id=user_id))

        try:
            user_service.toggle_system_admin(user_id, form.system_admin.data)
            if form.system_admin.data:
                flash(
                    "Usuario convertido en Administrador del sistema exitosamente",
                    "success",
                )
            else:
                flash("El usuario ya no es Administrador del sistema", "warning")
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error al actualizar Administrador del sistema: {str(e)}", "error")
    else:
        flash("Error en el formulario de Administrador del sistema", "error")

    return redirect(url_for("user_management.manage_user", user_id=user_id))
