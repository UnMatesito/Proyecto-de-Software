from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from core.services.historic_site_service import get_historic_site_by_id
from core.services import get_province_by_id, create_historic_site, get_category_by_id, get_tag_by_id, get_conservation_state_by_id, get_city_by_id, assign_relations_to_historic_site, get_user_by_id
from web.forms.historic_site import CreateSiteForm
import os
import folium

site_bp = Blueprint("site_bp", __name__, url_prefix="/sites")
"""
@site_bp.get("/")
def list_paginted_sites():
    try:
        order_by = request.args.get("order_by", "name")
        sorted_by = request.args.get("sorted_by", "asc")
        page = request.args.get("page", 1)
        pagination = get_paginated_tags(page=page, order_by=order_by, sorted_by=sorted_by)
        print(pagination)
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
"""
#Ver el detalle del site#
@site_bp.get("/datail/<int:site_id>")
def detail(site_id):
    try:
        print(site_id)
        site = get_historic_site_by_id(site_id)
        return render_template("historic_site/detail.html", site=site), 200
    except Exception as e:
        flash(f"Error al intentar ver detalle del tag, error: {e}", 400)
        return redirect("/sites")


@site_bp.get("/create")
def get_create():
    try:
        # --- Generar el mapa y guardarlo en static/maps/map_iframe.html ---
        map_dir = os.path.join("static", "maps")
        os.makedirs(map_dir, exist_ok=True)
        map_path = os.path.join(map_dir, "map_iframe.html")
        # Crear mapa

        m = folium.Map(location=[-34.6037, -58.3816], zoom_start=12)

        m.add_child(folium.LatLngPopup())
        map_name = m.get_name()  # ej: "m
        m.get_root().html.add_child(folium.Element(f"""
        <script>
        (function() {{
            function attach() {{
                var mapObj = window["{map_name}"];
                if (typeof mapObj === "undefined") {{
                    setTimeout(attach, 50);
                    return;
                }}
                // Al hacer click en el mapa enviamos las coordenadas al padre
                mapObj.on('click', function(e) {{
                    // En producción reemplazá "*" por el origen seguro del padre
                    window.parent.postMessage({{lat: e.latlng.lat, lng: e.latlng.lng}}, "*");
                }});
            }}
            attach();
        }})();
        </script>
        """))
        m.save(map_path)
        form = CreateSiteForm()
        return render_template("historic_site/create.html", form=form)
    except Exception as e:
        print(e)
        flash(f"Error al cargar el formulario {e}", "error")
        return redirect("/home"), 400
    
@site_bp.get("/cities/<int:province_id>")
def get_cities(province_id):
    province = get_province_by_id(province_id)
    return jsonify([{"id": c.id, "name": c.name} for c in province.cities])

@site_bp.post("/create")
def post_create():
    current_user =  get_user_by_id(session["user_id"])
    form = CreateSiteForm()
    if (form.validate_on_submit()):
        try:
            print(form.data)
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
            conservation_state = get_conservation_state_by_id(form.conservation_state.data)
            tags = []
            for tag_id in form.tags.data:
              tags.append(get_tag_by_id(tag_id))
            create_historic_site(**site)
            assign_relations_to_historic_site(conservation_state=conservation_state, category=category, city=city, user=current_user, tags=tags)
            return redirect("/create"), 200
        except Exception as e:  
            print(e)
            flash("Error al crear el sitio, {e}", "error")
            return redirect("/sites/create"), 400
    else:
        print(form.city.data)
        print(f"errro {form.errors}")
        flash(f"Error al crear el sitio", "error")
        return render_template("historic_site/create.html", form=form), 400
