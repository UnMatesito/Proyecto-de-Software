from flask import Blueprint, render_template, request, redirect, url_for, flash
from core.services.tag_service import get_all_tags, create_tag, get_paginated_tags
from web.forms.tag import CreateTagForm

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
    
@tag_bp.route("/create", methods=["GET", "POST"])
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
    elif (request.method == "GET"):
        return render_template("tags/create.html", form=form)
    else:
        flash(f"Error al crear tag: Datos invalidos", "error")
        return render_template("tags/create.html", form=form), 401
