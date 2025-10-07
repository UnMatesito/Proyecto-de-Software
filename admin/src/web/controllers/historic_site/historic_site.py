from flask import (
    Blueprint,
    Response,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from core.services import (
    assign_relations_to_historic_site,
    create_historic_site,
    delete_historic_site,
    get_all_cities,
    get_all_conservation_state,
    get_all_provinces,
    get_all_tags,
    get_category_by_id,
    get_city_by_id,
    get_conservation_state_by_id,
    get_historic_site_by_id,
    get_province_by_id,
    get_sites_filtered,
    get_tag_by_id,
    get_user_by_id,
    restore_historic_site,
    update_historic_site,
    validate,
)
from core.utils.export import export_sites_to_csv, get_csv_filename
from web.forms.historic_site import CreateSiteForm, EditSiteForm
from web.utils.auth import login_required, permission_required

site_bp = Blueprint("site_bp", __name__, url_prefix="/sites")


@site_bp.get("/")
@login_required
@permission_required("site_index")
def list_paginated_sites():
    try:
        # Obtener tags como string separado por comas y convertir a lista
        tags_param = request.args.get("tag_id", "")
        tags_id = [tid.strip() for tid in tags_param.split(",") if tid.strip()]

        order_by = request.args.get("order_by", "name")
        sorted_by = request.args.get("sorted_by", "asc")
        page = request.args.get("page", 1)

        search_filters = {
            "search_text": request.args.get("search_text"),
            "province_id": request.args.get("province_id"),
            "city_id": request.args.get("city_id"),
            "conservation_state_id": request.args.get("conservation_state_id"),
            "is_visible": request.args.get("is_visible"),
            "date_from": request.args.get("date_from"),
            "date_to": request.args.get("date_to"),
        }

        if tags_id:
            search_filters["tags_id"] = [int(tid) for tid in tags_id]

        pagination = get_sites_filtered(
            filters=search_filters,
            order_by=order_by,
            sorted_by=sorted_by,
            paginate=True,
            page=page,
            per_page=25,
        )

        sites = pagination["items"]

        columns = [
            {"key": "name", "label": "Nombre"},
            {
                "key": "city.province.name",
                "label": "Provincia",
                "render": lambda site: site.city.province.name,
            },
            {"key": "city", "label": "Ciudad", "render": lambda site: site.city.name},
            {"key": "brief_description", "label": "Descripción breve"},
            {
                "key": "conservation_state.state",
                "label": "Estado de conservación",
                "render": lambda site: site.conservation_state.state,
            },
            {"key": "created_at", "label": "Creado el", "render": "date"},
            {"key": "is_visible", "label": "Visibilidad"},
            {"key": "deleted_at", "label": "Estado", "render": "status"},
        ]

        cities = get_all_cities()
        city_choices = [(city.id, city.name) for city in cities]

        provinces = get_all_provinces()
        province_choices = [(province.id, province.name) for province in provinces]

        conservation_states = get_all_conservation_state()
        conservation_state_choices = [
            (state.id, state.state) for state in conservation_states
        ]

        tags = get_all_tags()
        tag_choices = [(tag.id, tag.name) for tag in tags]

        selected_tags = tags_id

        return render_template(
            "historic_site/index.html",
            sites=sites,
            order_by=order_by,
            sorted_by=sorted_by,
            pagination=pagination,
            columns=columns,
            filters=search_filters,
            province_choices=province_choices,
            conservation_state_choices=conservation_state_choices,
            city_choices=city_choices,
            tag_choices=tag_choices,
            selected_tags=selected_tags,
        )
    except Exception as e:
        flash(f"Error al cargar los sitios, error: {e}", "error")
        return redirect(url_for("main_bp.home"))


# Ver el detalle del site
@site_bp.get("/detail/<int:site_id>")
@login_required
@permission_required("site_show")
def detail(site_id):
    try:
        site = get_historic_site_by_id(site_id)
        province = get_province_by_id(site.city.province.id)
        lon = float(site.longitude)
        lat = float(site.latitude)
        return render_template(
            "historic_site/detail.html",
            site=site,
            lat=lat,
            lon=lon,
            province=province,
            site_name=site.name,
        )
    except Exception as e:
        flash(f"Error al intentar ver detalle del tag, error: {e}", "error")
        return redirect(url_for("site_bp.list_paginated_sites"))


@site_bp.get("/create")
@login_required
@permission_required("site_new")
def get_create():
    try:
        form = CreateSiteForm()
        return render_template("historic_site/create.html", form=form)
    except Exception as e:
        flash(f"Error al cargar el formulario, error: {e}", "error")
        return redirect(url_for("site_bp.list_paginated_sites"))


@site_bp.post("/create")
@login_required
@permission_required("site_new")
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
            assign_relations_to_historic_site(
                historic_site=site,
                conservation_state=conservation_state,
                category=category,
                city=city,
                user=current_user,
                tags=tags,
            )
            flash("Se creo correctamente el sitio", "success")
            return redirect(url_for("site_bp.list_paginated_sites"))
        except Exception as e:
            flash(f"Error al crear el sitio, {e}", "error")
            return redirect(url_for("site_bp.get_create"))
    else:
        flash(f"Error al crear el sitio", "error")
        return render_template("historic_site/create.html", form=form)


@site_bp.get("/edit/<int:site_id>")
@login_required
@permission_required("site_update")
def get_edit(site_id):
    try:
        site = get_historic_site_by_id(site_id=site_id)
        site_name = site.name
        form = EditSiteForm(site=site)

        # Cargo tags del sitio
        tags = site.tags
        tags_id = []
        for tag in tags:
            tags_id.append(tag.id)
        if tags:
            form.tags.data = tags_id

        lon = float(site.longitude)
        lat = float(site.latitude)

        return render_template(
            "historic_site/edit.html", form=form, lat=lat, lon=lon, site_name=site_name
        )
    except Exception as e:
        flash(f"Se produjo un error, {e}", "error")
        return redirect(url_for("site_bp.list_paginated_sites"))


@site_bp.post("/edit/<int:site_id>")
@login_required
@permission_required("site_update")
def post_edit(site_id):
    form = EditSiteForm()
    if form.validate_on_submit():
        try:
            body = {
                "historic_site_id": site_id,
                "name": form.name.data,
                "brief_description": form.brief_description.data,
                "full_description": form.full_description.data,
                "inauguration_year": form.inauguration_year.data,
                "location": {
                    "lat": form.latitude.data,
                    "lon": form.longitude.data,
                },
                "is_visible": form.is_visible.data,
                "city": form.city.data,
                "conservation_state": form.conservation_state.data,
                "category": form.category.data,
                "tags": form.tags.data,
            }
            update_historic_site(body)
            flash(f"El sitio {site_id} fue eliminado exitosamente", "success")
            return redirect(url_for("site_bp.list_paginated_sites"))
        except Exception as e:
            flash(
                f"Se produjo un error al intentar editar el sitio {site_id}, {e}",
                "error",
            )
            return redirect(url_for("site_bp.list_paginated_sites"))
    else:
        for e in form.errors:
            flash(
                f"Se produjo un error al intentar editar el sitio {site_id}, error: {e}",
                "error",
            )
        return redirect(url_for("site_bp.get_edit", site_id=site_id))


@site_bp.get("/delete/<int:site_id>")
@login_required
@permission_required("site_destroy")
def delete(site_id):
    try:
        delete_historic_site(site_id=site_id)
        flash(f"El sitio {site_id} fue eliminado exitosamente", "success")
        return redirect(url_for("site_bp.list_paginated_sites"))
    except Exception as e:
        flash(f"Error al intentar eliminar el sitio {site_id}, {e}", "error")
        return redirect(url_for("site_bp.list_paginated_sites"))


@site_bp.post("/restore/<int:site_id>")
@login_required
@permission_required("site_restore")
def restore(site_id):
    try:
        restore_historic_site(site_id=site_id)
        flash(f"El sitio {site_id} fue restaurado exitosamente", "success")
    except Exception as e:
        flash(f"Error al intentar restaurar el sitio {site_id}, {e}", "error")
    return redirect(url_for("site_bp.list_paginated_sites"))


@site_bp.get("/validate/<int:site_id>")
@login_required
@permission_required("proposal_approve")
def validate_site(site_id):
    try:
        validate(site_id=site_id)
        flash(f"Se valido correctamente el sitio {site_id}", "success")
    except Exception as e:
        flash(f"Error al intentar validar el sitio {site_id}, {e}", "error")
    return redirect(url_for("site_bp.list_paginated_sites"))


@site_bp.get("/export")
@login_required
@permission_required("site_export")
def export():
    try:
        order_by = request.args.get("order_by", "name")
        sorted_by = request.args.get("sorted_by", "asc")

        # Obtener tags como string separado por comas
        tags_param = request.args.get("tag_id", "")
        tags_id = []
        if tags_param:
            try:
                tags_id = [int(tid.strip()) for tid in tags_param.split(",") if tid.strip()]
            except ValueError:
                flash("IDs de tags inválidos", "error")
                return redirect(url_for("site_bp.list_paginated_sites"))

        # Procesar is_visible
        is_visible_value = None
        if "is_visible" in request.args:
            is_visible_value = True

        search_filters = {
            "search_text": request.args.get("search_text"),
            "province_id": request.args.get("province_id"),
            "city_id": request.args.get("city_id"),
            "conservation_state_id": request.args.get("conservation_state_id"),
            "is_visible": is_visible_value,
            "date_from": request.args.get("date_from"),
            "date_to": request.args.get("date_to"),
        }

        if tags_id:
            search_filters["tags_id"] = tags_id

        sitios = get_sites_filtered(
            filters=search_filters,
            order_by=order_by,
            sorted_by=sorted_by,
            paginate=False,
        )

        if not sitios:
            flash("No hay sitios para exportar con los filtros aplicados", "warning")
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
    except ValueError as e:
        flash(f"Error en los filtros: {str(e)}", "error")
        return redirect(url_for("site_bp.list_paginated_sites"))
    except Exception as e:
        flash(f"Error al exportar sitios: {str(e)}", "error")
        return redirect(url_for("site_bp.list_paginated_sites"))