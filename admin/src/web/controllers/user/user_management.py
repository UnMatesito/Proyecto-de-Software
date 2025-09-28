from flask import Blueprint, flash, redirect, render_template, url_for, request

from core.services import role_service, user_service
from web.forms.user import AssignRoleForm, BlockUserForm, ToggleSystemAdminForm
from web.utils.auth import login_required, permission_required, get_current_user

user_management_bp = Blueprint("user_management", __name__)


@user_management_bp.get("/users/<int:user_id>/manage")
@login_required
@permission_required("user_show")
def manage_user(user_id):
    """Página para gestionar roles y estado de un usuario específico"""
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
    """Asigna un rol a un usuario"""
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
            if not role or role.name not in ["Editor", "Administrador"]:
                flash("Rol no válido", "error")
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
                flash(f"Error en {field}: {error}", "error")

    return redirect(url_for("user_management.manage_user", user_id=user_id))


@user_management_bp.post("/users/<int:user_id>/remove-role")
@login_required
@permission_required("user_update")
def remove_role(user_id):
    """Quita el rol actual de un usuario (lo deja como Usuario público)"""
    try:
        # Verificar que el usuario existe
        user = user_service.get_user_by_id(user_id)
        if not user:
            flash("Usuario no encontrado", "error")
            return redirect(url_for("users.index"))

        # Obtener el rol de "Usuario público"
        public_role = role_service.get_role_by_name("Usuario público")
        if not public_role:
            flash('Error: No se encontró el rol "Usuario público"', "error")
            return redirect(url_for("user_management.manage_user", user_id=user_id))

        # Asignar rol público (esto efectivamente "quita" el rol administrativo)
        user_service.assign_role(user_id, public_role.id)
        flash(
            f"Rol administrativo removido. {user.email} ahora es Usuario público",
            "success",
        )

    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Error al remover el rol: {str(e)}", "error")

    return redirect(url_for("user_management.manage_user", user_id=user_id))


@user_management_bp.post("/users/<int:user_id>/toggle-block")
@login_required
@permission_required("user_update")
def toggle_block(user_id):
    """Bloquea o desbloquea un usuario"""
    form = BlockUserForm()

    if form.validate_on_submit():
        try:
            # Verificar que el usuario existe
            user = user_service.get_user_by_id(user_id)
            if not user:
                flash("Usuario no encontrado", "error")
                return redirect(url_for("users.index"))

            # Verificar que no es System Admin o Administrador si se intenta bloquear
            if form.block.data and user.system_admin:
                flash("No se puede bloquear a un usuario Administrador del sistema", "error")
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
    """Activa o desactiva el flag System Admin de un usuario"""
    form = ToggleSystemAdminForm()

    if form.validate_on_submit():
        current_user = get_current_user()
        if not current_user or not current_user.system_admin:
            flash("Solo un Administrador del sistema puede cambiar este valor", "error")
            return redirect(url_for("user_management.manage_user", user_id=user_id))

        try:
            user_service.toggle_system_admin(user_id, form.system_admin.data)
            if form.system_admin.data:
                flash("Usuario convertido en Administrador del sistema exitosamente", "success")
            else:
                flash("El usuario ya no es Administrador del sistema", "warning")
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error al actualizar Administrador del sistema: {str(e)}", "error")
    else:
        flash("Error en el formulario de Administrador del sistema", "error")

    return redirect(url_for("user_management.manage_user", user_id=user_id))