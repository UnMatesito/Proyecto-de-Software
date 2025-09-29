from flask import Blueprint, render_template, request, redirect, url_for, flash
from core.services.tag_service import get_all_tags, create_tag, get_paginated_tags, update_tag, get_tag_by_id, delete_tag
from web.forms.tag import CreateTagForm, EditTagForm, DeleteTagForm
from web.utils.auth import login_required, permission_required

tag_bp = Blueprint("tag_bp", __name__, url_prefix="/tags")


@tag_bp.route("/")
@login_required
def list_paginted_tags():
    try:
        deleteForm = DeleteTagForm()
        order_by = request.args.get("order_by", "name")
        sorted_by = request.args.get("sorted_by", "asc")
        page = request.args.get("page", 1)
        pagination = get_paginated_tags(page=page, order_by=order_by, sorted_by=sorted_by)
        print(pagination)
        columns = [
            {"key": "_name", "label": "Nombre"},
            {"key": "slug", "label": "Slug"},
            {"key": "created_at", "label": "Creado"},
            {"key": "deleted_at", "label": "Estado"}
        ]
        return render_template(
            "tags/index.html", 
            tags=pagination["items"], 
            order_by=order_by, 
            sorted_by=sorted_by, 
            pagination = pagination,
            columns=columns,
            deleteForm = deleteForm
        )
    except Exception as e:
        print(e)
        flash(f'Error al cargar tags: {str(e)}', 'error')
        return render_template("tags/index.html", tags = [], order_by = "name", sorted_by = "asc", urls=urls)
    
@tag_bp.post("/create")
@login_required
def create_tags():
    form = CreateTagForm()
    if form.validate_on_submit():
        try:
            print(form.name.data)
            create_tag(name=form.name.data)
            flash(f"Tag creado correctamente!", "success")
            return redirect("/tags")
        except Exception as e:
            flash(f"Error al crear tag: {e}", "error")
            return render_template("tags/create.html", form=form), 400
    else:
        flash(f"Error al crear tag: Datos invalidos", "error")
        return render_template("tags/create.html", form=form), 400

@tag_bp.get("/create")
@login_required
def show_create_tags():
    form = CreateTagForm()
    return render_template("tags/create.html", form = form), 200

@tag_bp.post("/delete/<int:tag_id>")
@login_required
def delete(tag_id):
        try:
            delete_tag(tag_id)
            flash(f"Se ah eliminado correctamente el tag {tag_id}", "succes")
            return redirect("/tags")
        except Exception as e:
            flash(f"Erro al intentar eliminar el tag {e}", "error")
            return redirect("/tags")

@tag_bp.post("/edit/<int:tag_id>")
@login_required
def edit_tag(tag_id):
    form = EditTagForm()
    if (form.validate_on_submit()):
        try:
            update_tag(tag_id, form.name.data)
            flash("Se ha actualizado correctamente el tag!", "succes")
            return redirect("/tags")
        except Exception as e:
            flash(f"Error al editar el tag {tag_id}, {e}", "error")
            return redirect("/tags") 
        
@tag_bp.get("/edit/<int:tag_id>")
@login_required
def show_edit_tag(tag_id): 
    try:
        form = EditTagForm()
        tag = get_tag_by_id(tag_id)
        return render_template("tags/edit.html", form=form, tag=tag)
    except Exception as e:
        flash(f"Error al seleccinar el tag {tag_id}: {e}", "error")
        return redirect("/tags")
    
@tag_bp.get("/datail/<int:tag_id>")
@login_required
@permission_required("user_show")
def detail_tag(tag_id):
    try:
        print(tag_id)
        tag = get_tag_by_id(tag_id)
        return render_template("tags/detail.html", tag=tag), 200
    except Exception as e:
        flash(f"Error al intentar ver detalle del tag, error: {e}", 400)
        return redirect("/tags/")
