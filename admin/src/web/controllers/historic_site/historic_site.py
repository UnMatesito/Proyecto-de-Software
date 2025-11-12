from flask import (
    Blueprint,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from core.services import (
    assign_relations_to_historic_site,
    create_historic_site,
    create_multiple_images,
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
    get_site_images,
    get_sites_filtered,
    get_tag_by_id,
    get_user_by_id,
    reorder_site_images,
    restore_historic_site,
    update_historic_site,
    validate_historic_site,
)
from core.utils.export import export_sites_to_csv, get_csv_filename
from web.forms.historic_site import CreateSiteForm, EditSiteForm, SiteImageUploadForm
from web.utils.auth import login_required, permission_required

site_bp = Blueprint("site_bp", __name__, url_prefix="/sites")


@site_bp.get("/")
@login_required
@permission_required("site_index")
def list_paginated_sites():
    """
    Muestra la lista paginada de sitios históricos con opciones de filtrado y ordenamiento.

    Este endpoint permite visualizar los sitios históricos con capacidades de:
    - Paginación (25 elementos por página)
    - Filtrado múltiple por diversos criterios
    - Ordenamiento por diferentes columnas
    - Búsqueda textual en nombre y descripción breve

    Parámetros URL:
        page (int): Número de página para paginación (default: 1)
        order_by (str): Campo para ordenar resultados (default: "name")
        sorted_by (str): Dirección de ordenamiento "asc" o "desc" (default: "asc")
        search_text (str): Texto para búsqueda en nombre y descripción breve
        province_id (int): ID de provincia para filtrar
        city_id (int): ID de ciudad para filtrar
        conservation_state_id (int): ID de estado de conservación
        is_visible (str): Filtro por visibilidad ("true" para visibles)
        date_from (str): Fecha desde para filtrar por creación (formato YYYY-MM-DD)
        date_to (str): Fecha hasta para filtrar por creación (formato YYYY-MM-DD)
        tag_id (str): IDs de tags separados por comas para filtro múltiple

    Returns:
        Response: Renderiza template con lista de sitios y datos para filtros

    Template:
        historic_site/index.html

    Contexto template:
        sites (list): Lista de sitios históricos de la página actual
        pagination (dict): Información de paginación
        columns (list): Configuración de columnas para la tabla
        filters (dict): Filtros aplicados actualmente
        order_by (str): Campo de ordenamiento actual
        sorted_by (str): Dirección de ordenamiento actual
        province_choices (list): Opciones para dropdown de provincias
        city_choices (list): Opciones para dropdown de ciudades
        conservation_state_choices (list): Opciones para dropdown de estados de conservación
        tag_choices (list): Opciones para dropdown de tags
        selected_tags (list): Tags seleccionados actualmente

    Raises:
        Exception: Si ocurre un error durante la carga de datos
    """
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
            text_search_columns=["name", "brief_description"],
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
            {"key": "is_visible", "label": "Visibilidad", "render": "visibility"},
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
    """Renderiza el detalle del sitio histórico al que pertenece el ID enviado por URL."""

    try:
        site = get_historic_site_by_id(site_id)
        province = get_province_by_id(site.city.province.id)
        images = get_site_images(site_id)
        lon = float(site.longitude)
        lat = float(site.latitude)
        return render_template(
            "historic_site/detail.html",
            site=site,
            images=images,
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
    """Renderiza el formulario para crear sitios históricos."""

    try:
        form = CreateSiteForm()
        image_form = SiteImageUploadForm(existing_images=0, require_images=True)
        return render_template(
            "historic_site/create.html",
            form=form,
            image_form=image_form,
        )
    except Exception as e:
        flash(f"Error al cargar el formulario, error: {e}", "error")
        return redirect(url_for("site_bp.list_paginated_sites"))


@site_bp.post("/create")
@login_required
@permission_required("site_new")
def post_create():
    """Recibe y verifica los datos enviados por el formulario de creacion."""
    current_user = get_user_by_id(session["user_id"])
    form = CreateSiteForm()
    image_form = SiteImageUploadForm(existing_images=0, require_images=True)

    form_valid = form.validate_on_submit()
    images_valid = image_form.validate()

    if not (form_valid and images_valid):
        form.city.choices = [
            (city.id, city.name)
            for city in get_all_cities()
            if (city.province_id == form.province.data)
        ]
        return render_template(
            "historic_site/create.html",
            form=form,
            image_form=image_form,
        )

    try:
        site_data = {
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

        # Crear el sitio
        site = create_historic_site(**site_data)
        assign_relations_to_historic_site(
            historic_site=site,
            conservation_state=conservation_state,
            category=category,
            city=city,
            user=current_user,
            tags=tags,
        )

        images = image_form.images.data
        if images:
            try:
                create_multiple_images(
                    historic_site_id=site.id,
                    files=images,
                    set_first_as_cover=True,
                    titles=image_form.image_titles.data,
                    descriptions=image_form.image_descriptions.data,
                )
                flash(
                    f"Se subieron {len(images)} imágenes correctamente",
                    "success",
                )
            except Exception as e:
                flash(f"Error al subir imágenes: {e}", "warning")

        flash("Se creó correctamente el sitio", "success")
        return redirect(url_for("site_bp.list_paginated_sites"))

    except Exception as e:
        flash(f"Error al crear el sitio, {e}", "error")
        return redirect(url_for("site_bp.get_create"))

@site_bp.get("/edit/<int:site_id>")
@login_required
@permission_required("site_update")
def get_edit(site_id):
    """Renderiza el formulario para modificar los sitios históricos."""

    try:
        site = get_historic_site_by_id(site_id=site_id)
        site_name = site.name
        images = get_site_images(site_id)
        form = EditSiteForm(site=site)
        image_form = SiteImageUploadForm(existing_images=len(images))

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
            "historic_site/edit.html",
            form=form,
            image_form=image_form,
            lat=lat,
            lon=lon,
            site_name=site_name,
            site=site,
            images=images,
        )
    except Exception as e:
        flash(f"Se produjo un error, {e}", "error")
        return redirect(url_for("site_bp.list_paginated_sites"))


@site_bp.post("/edit/<int:site_id>")
@login_required
@permission_required("site_update")
def post_edit(site_id):
    """Recibe y verifica los datos enviados por el formulario de edición."""
    site = get_historic_site_by_id(site_id=site_id)
    existing_images = get_site_images(site_id)
    form = EditSiteForm()
    image_form = SiteImageUploadForm(existing_images=len(existing_images))

    form_valid = form.validate_on_submit()
    images_valid = image_form.validate()

    if not (form_valid and images_valid):
        lat = float(site.latitude)
        lon = float(site.longitude)
        return render_template(
            "historic_site/edit.html",
            form=form,
            image_form=image_form,
            lat=lat,
            lon=lon,
            site_name=site.name,
            site=site,
            images=existing_images,
        )

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

        new_files = image_form.images.data
        if new_files:
            try:
                from core.services.site_image_service import create_site_image

                start_order = len(existing_images)
                created = []

                for index, (file, title, description) in enumerate(
                    zip(
                        new_files,
                        image_form.image_titles.data,
                        image_form.image_descriptions.data,
                    )
                ):
                    if not file or not getattr(file, "filename", ""):
                        continue

                    is_cover = start_order == 0 and index == 0
                    create_site_image(
                        historic_site_id=site_id,
                        file=file,
                        order=start_order + index,
                        is_cover=is_cover,
                        title=title,
                        description=description,
                    )
                    created.append(file.filename)

                if start_order == 0:
                    ordered_images = get_site_images(site_id)
                    reorder_site_images(
                        historic_site_id=site_id,
                        ordered_image_ids=[image.id for image in ordered_images],
                    )

                if created:
                    flash(f"Se agregaron {len(created)} imágenes", "success")
            except Exception as e:
                flash(f"Error al subir imágenes: {e}", "warning")

        flash(f"El sitio {form.name.data} fue editado exitosamente", "success")
        return redirect(url_for("site_bp.list_paginated_sites"))

    except Exception as e:
        flash(
            f"Se produjo un error al intentar editar el sitio {form.name.data}, {e}",
            "error",
        )
        return redirect(url_for("site_bp.list_paginated_sites"))


@site_bp.post("/delete/<int:site_id>")
@login_required
@permission_required("site_destroy")
def delete(site_id):
    """Recibe el id del un sitio histórico, si existe y
    no está borrado lo borra.
    """
    try:
        delete_historic_site(site_id=site_id)
        flash(f"El sitio {site_id} fue eliminado exitosamente", "success")
        return redirect(url_for("site_bp.list_paginated_sites"))
    except Exception as e:
        flash(f"Error al intentar eliminar el sitio {site_id}, {e}", "error")
        return redirect(url_for("site_bp.list_paginated_sites"))


@site_bp.post("/image/delete/<int:image_id>")
@login_required
@permission_required("site_update")
def delete_image(image_id):
    """Elimina una imagen específica de un sitio"""
    try:
        from core.models import SiteImage
        from core.services.site_image_service import delete_site_image

        image = SiteImage.query.get_or_404(image_id)
        site_id = image.historic_site_id

        delete_site_image(image_id)
        flash("Imagen eliminada correctamente", "success")

    except Exception as e:
        flash(f"Error al eliminar imagen: {e}", "error")

    return redirect(url_for("site_bp.get_edit", site_id=site_id))


@site_bp.post("/image/reorder/<int:site_id>")
@login_required
@permission_required("site_update")
def reorder_images(site_id):
    """Actualiza el orden de las imágenes utilizando arrastrar y soltar."""

    payload = request.get_json(silent=True) or {}
    ordered_ids = payload.get("ordered_image_ids")

    if not isinstance(ordered_ids, list) or not ordered_ids:
        return jsonify({"error": "Se requiere un listado de imágenes."}), 400

    try:
        casted_ids = [int(image_id) for image_id in ordered_ids]
    except (TypeError, ValueError):
        return jsonify({"error": "Los identificadores de las imágenes no son válidos."}), 400

    try:
        reorder_site_images(historic_site_id=site_id, ordered_image_ids=casted_ids)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:  # pragma: no cover - fallback de error
        return jsonify({"error": f"No se pudo actualizar el orden: {exc}"}), 500

    return jsonify({"status": "ok"}), 200


@site_bp.post("/image/<int:image_id>/cover")
@login_required
@permission_required("site_update")
def set_image_cover(image_id):
    """Establece la portada de un sitio histórico."""
    from core.models import SiteImage

    image = SiteImage.query.get_or_404(image_id)
    site_id = image.historic_site_id

    try:
        ordered_images = get_site_images(site_id)
        ordered_ids = [image_id] + [img.id for img in ordered_images if img.id != image_id]
        reorder_site_images(historic_site_id=site_id, ordered_image_ids=ordered_ids)
        flash("La portada del sitio se actualizó correctamente", "success")
    except Exception as e:
        flash(f"Error al actualizar la portada: {e}", "error")

    return redirect(url_for("site_bp.get_edit", site_id=site_id))


@site_bp.post("/image/<int:image_id>/move")
@login_required
@permission_required("site_update")
def move_image(image_id):
    """Reordena una imagen moviéndola una posición."""
    from core.models import SiteImage

    direction = request.form.get("direction")
    if direction not in {"up", "down"}:
        flash("Dirección de movimiento inválida", "error")
        return redirect(request.referrer or url_for("site_bp.list_paginated_sites"))

    image = SiteImage.query.get_or_404(image_id)
    site_id = image.historic_site_id

    try:
        ordered_images = get_site_images(site_id)
        positions = {img.id: index for index, img in enumerate(ordered_images)}
        current_index = positions.get(image_id)

        if current_index is None:
            flash("No se pudo determinar la posición de la imagen", "error")
            return redirect(url_for("site_bp.get_edit", site_id=site_id))

        if direction == "up" and current_index == 0:
            flash("La imagen ya se encuentra en la primera posición", "info")
            return redirect(url_for("site_bp.get_edit", site_id=site_id))

        if direction == "down" and current_index == len(ordered_images) - 1:
            flash("La imagen ya se encuentra en la última posición", "info")
            return redirect(url_for("site_bp.get_edit", site_id=site_id))

        target_index = current_index - 1 if direction == "up" else current_index + 1
        ordered_ids = [img.id for img in ordered_images]
        ordered_ids[current_index], ordered_ids[target_index] = (
            ordered_ids[target_index],
            ordered_ids[current_index],
        )

        reorder_site_images(historic_site_id=site_id, ordered_image_ids=ordered_ids)

        flash("El orden de las imágenes se actualizó correctamente", "success")
    except Exception as e:
        flash(f"Error al reordenar la imagen: {e}", "error")

    return redirect(url_for("site_bp.get_edit", site_id=site_id))


@site_bp.post("/restore/<int:site_id>")
@login_required
@permission_required("site_restore")
def restore(site_id):
    """Recibe el id del un sitio histórico, si existe y
    está borrado lo restaura.
    """
    try:
        restore_historic_site(site_id=site_id)
        flash(f"El sitio {site_id} fue restaurado exitosamente", "success")
    except Exception as e:
        flash(f"Error al intentar restaurar el sitio {site_id}, {e}", "error")
    return redirect(url_for("site_bp.list_paginated_sites"))


@site_bp.get("/validate/<int:site_id>")
@login_required
@permission_required("proposal_approve")
def validate(site_id):
    """Recibe el id del un sitio histórico, si existe y
    está borrado lo válida.
    """
    try:
        validate_historic_site(site_id=site_id)
        flash(f"Se valido correctamente el sitio {site_id}", "success")
    except Exception as e:
        flash(f"Error al intentar validar el sitio {site_id}, {e}", "error")
    return redirect(url_for("site_bp.list_paginated_sites"))


@site_bp.get("/export")
@login_required
@permission_required("site_export")
def export():
    """
    Exporta sitios históricos a formato CSV según filtros aplicados.

    Procesa múltiples parámetros de filtrado (búsqueda textual, provincia, ciudad,
    estado de conservación, visibilidad, fechas y tags) para generar un archivo CSV
    con los sitios que coincidan con los criterios especificados.

    Parámetros URL:
        order_by (str): Campo para ordenar los resultados (default: "name")
        sorted_by (str): Dirección del ordenamiento "asc" o "desc" (default: "asc")
        search_text (str): Texto para búsqueda en nombre y descripción
        province_id (int): ID de provincia para filtrar
        city_id (int): ID de ciudad para filtrar
        conservation_state_id (int): ID de estado de conservación
        is_visible (bool): Filtro por visibilidad del sitio
        date_from (str): Fecha desde para filtrar por creación
        date_to (str): Fecha hasta para filtrar por creación
        tag_id (str): IDs de tags separados por comas

    Returns:
        Response: Archivo CSV para descarga o redirección con mensaje flash

    Raises:
        ValueError: Si los parámetros de filtrado son inválidos
        Exception: Si ocurre un error durante la exportación
    """
    try:
        order_by = request.args.get("order_by", "name")
        sorted_by = request.args.get("sorted_by", "asc")

        # Obtener tags como string separado por comas
        tags_param = request.args.get("tag_id", "")
        tags_id = []
        if tags_param:
            try:
                tags_id = [
                    int(tid.strip()) for tid in tags_param.split(",") if tid.strip()
                ]
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