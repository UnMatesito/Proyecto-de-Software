from flask import Blueprint, flash, redirect, render_template, request, url_for

from core.services.tag_service import (
    create_tag,
    delete_tag,
    get_paginated_tags,
    get_tag_by_id,
    get_tag_by_name,
    update_tag,
    get_total_tags_count
)
from web.forms.tag import CreateTagForm, EditTagForm
from web.utils.auth import login_required, permission_required

tag_bp = Blueprint("tag_bp", __name__, url_prefix="/tags")


@tag_bp.get("/")
@login_required
@permission_required("tag_index")
def list_paginated_tags():
    """Renderiza el index.html de los tags mostrandolos en formato paginado,
    el cual puede estar ordenado por nombre o fecha de creación
    y de manera ascendente o descendente.

    columns: Representa las columnas mostradas en la tabla del index.html.
    order_by: nombre o fecha de creación
    sorted_by: ascendente o descendente.
    page: Pagina acutal, inicialmente en 1
    pagination: Diccionario que posee los elementos necesarios para la paginación.
    tag: Se utiliza para recibir y mostrar un tag en particular.
    """
    try:
        name = request.args.get("name", None)
        order_by = request.args.get("order_by", "name")
        sorted_by = request.args.get("sorted_by", "asc")
        page = request.args.get("page", 1)
        pagination = get_paginated_tags(
            page=page, order_by=order_by, sorted_by=sorted_by, name=name
        )
        total_tags = get_total_tags_count()
        columns = [
            {"key": "name", "label": "Nombre"},
            {"key": "slug", "label": "Slug"},
            {"key": "created_at", "label": "Creado", "render": "date"},
            {"key": "deleted_at", "label": "Estado", "render": "status"},
        ]
        return render_template(
            "tags/index.html",
            tags=pagination["items"],
            order_by=order_by,
            sorted_by=sorted_by,
            pagination=pagination,
            columns=columns,
            total_tags=total_tags,
        )
    except Exception as e:
        flash(f"Error al cargar tags: {str(e)}", "error")
        return render_template(
            "tags/index.html", tags=[], order_by="name", sorted_by="asc"
        )


@tag_bp.get("/create")
@login_required
@permission_required("tag_new")
def show_create_tags():
    """Renderiza el formulario para crear tags."""

    form = CreateTagForm()
    return render_template("tags/create.html", form=form)


@tag_bp.post("/create")
@login_required
@permission_required("tag_new")
def create_tags():
    """Recibe y verifica los datos enviados por el formulario de creacion.
    Si los datos enviados son válidos hace el alta del tag.
    """
    form = CreateTagForm()
    if form.validate_on_submit():
        try:
            create_tag(name=form.name.data)
            flash("Tag creado correctamente!", "success")
            return redirect(url_for("tag_bp.list_paginated_tags"))
        except Exception as e:
            flash(f"Error al crear tag: {e}", "error")
            return render_template("tags/create.html", form=form)
    else:
        flash("Error al crear tag: Datos invalidos", "error")
        return render_template("tags/create.html", form=form)


@tag_bp.get("/edit/<int:tag_id>")
@login_required
@permission_required("tag_update")
def show_edit_tag(tag_id):
    """Renderiza el formulario para modificar los tags."""

    try:
        form = EditTagForm()
        tag = get_tag_by_id(tag_id)
        return render_template("tags/edit.html", form=form, tag=tag)
    except Exception as e:
        flash(f"Error al seleccinar el tag, {e}", "error")
        return redirect(url_for("tag_bp.list_paginated_tags"))


@tag_bp.post("/edit/<int:tag_id>")
@login_required
@permission_required("tag_update")
def edit_tag(tag_id):
    """Recibe y verifica los datos enviados por el formulario de edición.
    Si los datos enviados son válidos hace el edit del tag.
    """
    form = EditTagForm()
    if form.validate_on_submit():
        try:
            tag = update_tag(tag_id, form.name.data)
            flash("Se ha actualizado correctamente el tag!", "succes")
        except Exception as e:
            flash(f"Error al editar el tag, {e}", "error")
        return redirect(url_for("tag_bp.list_paginated_tags"))
    else:
        try:
            tag = get_tag_by_id(tag_id)
            return render_template("tags/edit.html", form=form, tag=tag)
        except Exception as e:
            flash(f"Error al editar el tag, {e}", "error")
            return redirect(url_for("tag_bp.list_paginated_tags"))


@tag_bp.post("/delete/<int:tag_id>")
@login_required
@permission_required("tag_destroy")
def delete(tag_id):
    """Recibe el id del un tag, si existe y no se posee sitios
    históricos asociados lo borra.
    """
    try:
        tag = delete_tag(tag_id)
        flash(f"Se ha eliminado correctamente el tag {tag.name}", "succes")
    except Exception as e:
        flash(f"Error al intentar eliminar el tag: {e}", "error")
    return redirect(url_for("tag_bp.list_paginated_tags"))


@tag_bp.get("/detail/<int:tag_id>")
@login_required
@permission_required("tag_show")
def detail_tag(tag_id):
    """Renderiza el detalle del tag al que pertenece el ID enviado por URL."""

    try:
        tag = get_tag_by_id(tag_id)
        return render_template("tags/detail.html", tag=tag)
    except Exception as e:
        flash(f"Error al intentar ver detalle del tag, error: {e}", "error")
        return redirect(url_for("tag_bp.list_paginated_tags"))
