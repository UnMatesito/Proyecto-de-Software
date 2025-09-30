import os
from bs4 import BeautifulSoup
import folium
from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
    Response
)

from core.services import (
    assign_relations_to_historic_site,
    create_historic_site,
    get_category_by_id,
    get_city_by_id,
    get_conservation_state_by_id,
    get_province_by_id,
    get_tag_by_id,
    get_user_by_id,
    get_sites_filtered,
    get_historic_site_by_id
)
from core.utils.export import export_sites_to_csv, get_csv_filename
from web.forms.historic_site import CreateSiteForm
from web.utils.auth import login_required, permission_required

site_bp = Blueprint("site_bp", __name__, url_prefix="/sites")

@site_bp.get("/")
def list_paginated_sites():
    try:
        order_by = request.args.get("order_by", "name")
        sorted_by = request.args.get("sorted_by", "asc")
        page = request.args.get("page", 1)

        pagination = get_sites_filtered(
            filters=request.args,
            order_by=order_by,
            sorted_by=sorted_by,
            paginate=True,
            page=page,
            per_page=25,
        )

        # Armamos columnas para la tabla
        columns = [
            {"key": "name", "label": "Nombre"},
            {"key": "city.name", "label": "Ciudad"},
            {"key": "city.province.name", "label": "Provincia"},
            {"key": "conservation_state.state", "label": "Estado de conservación"},
            {"key": "is_visible", "label": "Visibilidad"},
        ]

        sites = pagination["items"]

        return render_template(
            "historic_site/index.html",
            sites=sites,
            order_by=order_by,
            sorted_by=sorted_by,
            pagination=pagination,
            columns=columns,
        )
    except Exception as e:
        flash(f"Error al cargar los sitios: {e}", "error")
        return redirect("/home"), 400

# Ver el detalle del site#
@site_bp.get("/detail/<int:site_id>")
def detail(site_id):
    try:
        site = get_historic_site_by_id(site_id)
        province = get_province_by_id(site.city.province.id)
        lon = float(site.longitude)
        lat = float(site.latitude)
        map = folium.Map(location=[lat, lon], zoom_start=17)
        folium.Marker(location=[lat, lon], popup=folium.Popup(site.name, show=True)).add_to(map)
        map_html = map._repr_html_()
        return render_template("historic_site/detail.html", site=site, map=map_html, province=province), 200
    except Exception as e:
        print(e)
        flash(f"Error al intentar ver detalle del tag, error: {e}", "error")
        return redirect("/sites")


@site_bp.get("/create")
@login_required
def get_create():
    try:
        m = folium.Map(location=[-34.9205, -57.9536], zoom_start=12)
        m.add_child(folium.LatLngPopup())
        map_name = m.get_name()

        map_html = m.get_root().render()
        # Extraer solo el contenido del body (mapa + scripts)
        print(map_html)
        form = CreateSiteForm()
        return render_template("historic_site/create.html", form=form, map_html=map_html, map_name=map_name)
    except Exception as e:
        flash(f"Error al cargar el formulario {e}", "error")
        return redirect("/home"), 400


@site_bp.get("/cities/<int:province_id>")
def get_cities(province_id):
    province = get_province_by_id(province_id)
    return jsonify([{"id": c.id, "name": c.name} for c in province.cities])


@site_bp.post("/create")
@login_required
def post_create():
    current_user = get_user_by_id(session["user_id"])
    form = CreateSiteForm()
    if form.validate_on_submit():
        try:
            site = {
                "name": form.name.data,
                "brief_description": form.brief_description.data,
                "full_description": form.full_description.data,
                "inauguration_year": form.inauguration_year.data,
                "latitude": form.latitude.data,
                "longitude": form.longitude.data,
            }
            city = get_city_by_id(form.city.data)
            category = get_category_by_id(form.category.data)
            conservation_state = get_conservation_state_by_id(
                form.conservation_state.data
            )
            tags = []
            for tag_id in form.tags.data:
                tags.append(get_tag_by_id(tag_id))
            site = create_historic_site(**site)
            flash("Se creo correctamente el sitio", "success")
            assign_relations_to_historic_site(
                historic_site=site,
                conservation_state=conservation_state,
                category=category,
                city=city,
                user=current_user,
                tags=tags,
            )
            return redirect(url_for("site_bp.list_paginated_sites"))
        except Exception as e:  
            print(e)
            flash(f"Error al crear el sitio, {e}", "error")
            return redirect("/sites/create"), 400
    else:
        flash(f"Error al crear el sitio", "error")
        return render_template("historic_site/create.html", form=form), 400

@site_bp.get("/export")
@login_required
@permission_required("site_export")
def export():
    try:
        order_by = request.args.get("order_by", "name")
        sorted_by = request.args.get("sorted_by", "asc")
        filters = request.args.to_dict()

        sitios = get_sites_filtered(
            filters=filters,
            order_by=order_by,
            sorted_by=sorted_by,
            paginate=False,
        )

        if not sitios:
            flash("No hay datos para exportar", "warning")
            return redirect(url_for("site_bp.list_paginated_sites"))

        csv_content = export_sites_to_csv(sitios)
        filename = get_csv_filename()

        return Response(
            csv_content,
            mimetype="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "text/csv; charset=utf-8",
            },
        )
    except Exception as e:
        flash(f"Error al exportar sitios: {e}", "error")
        return redirect(url_for("site_bp.list_paginated_sites"))
