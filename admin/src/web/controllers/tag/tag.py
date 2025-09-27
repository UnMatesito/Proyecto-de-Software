from flask import Blueprint, render_template, request, redirect, url_for, flash
from core.services.tag_service import get_all_tags, create_tag, get_paginated_tags, update_tag, get_tag_by_id
from web.forms.tag import CreateTagForm, EditTagForm

tag_bp = Blueprint("tag_bp", __name__, url_prefix = "/tags")

@tag_bp.route("/")
def list_paginted_tags():
    try:
        order_by = request.args.get("order_by", "name")
        sorted_by = request.args.get("sorted_by", "asc")
        page = request.args.get("page", 1)
        tags = get_paginated_tags(page=page, order_by=order_by, sorted_by=sorted_by)
        print(tags)
        return render_template("tags/index.html", tags = tags, order_by = order_by, sorted_by = sorted_by )
    except Exception as e:
        print(e)
        flash(f'Error al cargar tags: {str(e)}', 'error')
        return render_template("tags/index.html", tags = [], order_by = "name", sorted_by = "asc")
    
@tag_bp.post("/create")
def create_tags():
    form = CreateTagForm()
    if form.validate_on_submit():
        try:
            create_tag(name=form.name.data)
            flash(f"Tag creado correctamente!", "success")
            return redirect("/tags")
        except Exception as e:
            flash(f"Error al crear tag: {e}", "error")
            return redirect("/tags/create")
    else:
        flash(f"Error al crear tag: Datos invalidos", "error")
        return render_template("tags/create.html", form=form), 401

@tag_bp.get("/create")
def show_create_tags():
    form = CreateTagForm()
    return render_template("tags/create.html", form = form), 200

@tag_bp.post("/delete")
def delete_tag():
    return redirect("/tags")

@tag_bp.post("/activete")
def active_tag():
    return redirect("/tags")

@tag_bp.post("/edit/<int:tag_id>")
def edit_tag(tag_id):
    form = EditTagForm()
    if (form.validate_on_submit()):
        try:
            update_tag(tag_id, form.name.data)
            flash("Se ha actualizado correctamente el tag!", "succes")
            return redirect("/tags")
        except Exception as e:
            flash(f"Error al editar el tag {e}", "error")
            return redirect("/tags") 
        
@tag_bp.get("/edit/<int:tag_id>")
def show_edit_tag(tag_id): 
    try:
        form = EditTagForm()
        tag = get_tag_by_id(tag_id)
        return render_template("tags/edit.html", form=form, tag=tag)
    except Exception as e:
        flash(f"Error al seleccinar el tag {e}", "error")
        return redirect("/tags")
    
@tag_bp.get("/dailt/")
def detail_tag():
    try:
        tag_id = request.args.get("tag_id")
        tag = get_tag_by_id(tag_id)
        return render_template("tags/detail.html", tag=tag), 200
    except Exception as e:
        flash(f"Error al intentar modificar el tag, error: {e}", 400)
        return redirect("/tags/")
