from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from core.services.historic_site_service import get_historic_site_by_id
from core.services import get_province_by_id, create_historic_site, get_paginated_tags
from web.forms.historic_site import CreateSiteForm

site_bp = Blueprint("site_bp", __name__, url_prefix="/sites")

@site_bp.get("/")
def list_paginted_sites():
    try:
        order_by = request.args.get("order_by", "name")
        sorted_by = request.args.get("sorted_by", "asc")
        page = request.args.get("page", 1)
        pagination = get_paginated_tags(page=page, order_by=order_by, sorted_by=sorted_by)
        columns = [
            {"key": "name", "label": "Nombre"},
            {"key": "city", "label": "Ciudad"},
            {"key": "created_at", "label": "Provincia"},
            {"key": "conservation_state", "label": "Estado de conservación"},
            {"key": "is_visibility", "label": "VIsibilidad"}
        ]
        sites = pagination["items"]
        return render_template(
            "historic_site/index.html", 
            sites=sites, 
            order_by=order_by, 
            sorted_by=sorted_by, 
            pagination = pagination, # Objeto de paginacion #
            columns=columns,
        )
    except Exception as e:
        flash(f"Error al cargas los tags {e}", "error")
        return redirect("/home"), 400

#Ver el detalle del site#
@site_bp.get("/datail/<int:site_id>")
def detail(site_id):
    try:
        site = get_historic_site_by_id(site_id)
        return render_template("historic_site/detail.html", site=site), 200
    except Exception as e:
        flash(f"Error al intentar ver detalle del tag, error: {e}", 400)
        return redirect("/sites")

@site_bp.get("/create")
def get_create():
    try:
        form = CreateSiteForm()
        return render_template("historic_site/create.html", form=form)
    except Exception as e:
        flash(f"Error al cargar el formulario {e}", "error")
        return redirect("/home"), 400
    

@site_bp.get("/cities/<int:province_id>")
def get_cities(province_id):
    province = get_province_by_id(province_id)
    return jsonify([{"id": c.id, "name": c.name} for c in province.cities])

@site_bp.post("/create")
def post_create():
    form = CreateSiteForm()
    if (form.validate_on_submit()):
        try:
            site = {
                "name": form.name.data,
                "brief_description": form.brief_description.data,
                "full_description": form.full_description.data,
                "inauguration_year": form.inauguration_year.data,
                "province_id": form.province.data,
                "city_id": form.city.data,
                "conservation_state_id": form.conservation_state.data,
                "category_id": form.category.data,
            }
            create_historic_site(form.name)
            return redirect("/create"), 200
        except Exception as e:  
            flash("Error al crear el sitio, {e}", "error")
            return redirect("/sites/create"), 400
    else:
        flash(f"Error al crear el sitio", "error")
        return render_template("historic_site/create.html", form=form), 400
