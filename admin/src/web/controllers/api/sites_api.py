from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.services import historic_site_service, conservation_state_service
from core.database import db
from geoalchemy2.functions import ST_X, ST_Y
from . import api_bp


@api_bp.get("/sites")
def list_sites():
    """
    GET /sites
    Lista sitios históricos con filtros combinables según el PDF de la API.

    Parámetros:
      - name, description: búsqueda parcial (case-insensitive)
      - city, province: exactos (case-insensitive)
      - tags: separados por coma
      - order_by: latest | oldest | rating-5-1 | rating-1-5
      - lat, long, radius: búsqueda geoespacial
      - page, per_page: paginación
    """
    try:
        # Obtener parámetros
        name = request.args.get("name")
        description = request.args.get("description")
        city_name = request.args.get("city")
        province_name = request.args.get("province")
        tags_str = request.args.get("tags")
        order_by = request.args.get("order_by", "latest")

        # Parámetros geoespaciales (por ahora no soportados, se pueden agregar después)
        lat = request.args.get("lat", type=float)
        lon = request.args.get("long", type=float)
        radius = request.args.get("radius", type=float)

        # Parámetros de paginación
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        # Validaciones de paginación
        if page < 1:
            return jsonify({
                "error": {
                    "code": "invalid_query",
                    "message": "Parameter validation failed",
                    "details": {"page": ["Must be at least 1"]}
                }
            }), 400

        if per_page < 1 or per_page > 100:
            return jsonify({
                "error": {
                    "code": "invalid_query",
                    "message": "Parameter validation failed",
                    "details": {"per_page": ["Must be between 1 and 100"]}
                }
            }), 400

        # Validar parámetros geoespaciales
        if (lat is not None or lon is not None or radius is not None):
            if lat is None or lon is None or radius is None:
                return jsonify({
                    "error": {
                        "code": "invalid_query",
                        "message": "Parameter validation failed",
                        "details": {
                            "lat": ["Required when using geospatial search"],
                            "long": ["Required when using geospatial search"],
                            "radius": ["Required when using geospatial search"]
                        }
                    }
                }), 400

            if not (-90 <= lat <= 90):
                return jsonify({
                    "error": {
                        "code": "invalid_query",
                        "message": "Parameter validation failed",
                        "details": {"lat": ["Must be a valid latitude"]}
                    }
                }), 400

            if not (-180 <= lon <= 180):
                return jsonify({
                    "error": {
                        "code": "invalid_query",
                        "message": "Parameter validation failed",
                        "details": {"long": ["Must be a valid longitude"]}
                    }
                }), 400

        # Construir filtros para el servicio
        filters = {}

        # Filtros de texto: usar search_text del servicio
        search_terms = []
        if name:
            search_terms.append(name)
        if description:
            search_terms.append(description)

        if search_terms:
            # El servicio busca en todas las columnas de texto
            filters["search_text"] = " ".join(search_terms)

        # Filtros exactos
        if city_name:
            # Necesitamos buscar el city_id primero
            from core.models import City
            city = City.query.filter(
                db.func.lower(City.name) == city_name.lower()
            ).first()
            if city:
                filters["city_id"] = city.id

        if province_name:
            # Necesitamos buscar el province_id primero
            from core.models import Province
            province = Province.query.filter(
                db.func.lower(Province.name) == province_name.lower()
            ).first()
            if province:
                filters["province_id"] = province.id

        # Filtro por tags
        if tags_str:
            tag_list = [t.strip() for t in tags_str.split(",") if t.strip()]
            if tag_list:
                # Convertir slugs a IDs
                from core.models import Tag
                tag_ids = []
                for slug in tag_list:
                    tag = Tag.query.filter_by(slug=slug).first()
                    if tag:
                        tag_ids.append(tag.id)

                if tag_ids:
                    filters["tags_id"] = tag_ids

        # Filtros de visibilidad: solo sitios publicados (visible, validado, no eliminado)
        filters["is_visible"] = True
        filters["pending_validation"] = False
        # deleted_at debe ser NULL, pero el servicio no lo filtra automáticamente
        # Lo haremos después en el query

        # Mapear order_by del PDF al formato del servicio
        service_order_by = "created_at"  # Por defecto
        service_sorted_by = "desc"  # Por defecto latest

        if order_by == "latest":
            service_order_by = "created_at"
            service_sorted_by = "desc"
        elif order_by == "oldest":
            service_order_by = "created_at"
            service_sorted_by = "asc"
        elif order_by in ["rating-5-1", "rating-1-5"]:
            # TODO: Implementar cuando se agregue rating promedio
            # Por ahora mantener el orden por fecha
            pass

        # Usar el servicio para obtener sitios filtrados
        result = historic_site_service.get_sites_filtered(
            filters=filters,
            order_by=service_order_by,
            sorted_by=service_sorted_by,
            paginate=True,
            page=page,
            per_page=per_page
        )

        # Formatear respuesta según el PDF
        data = []
        for site in result["items"]:
            # Verificar que no esté eliminado
            if site.deleted_at is not None:
                continue

            # Extraer coordenadas del campo geometry
            lat_value = db.session.scalar(ST_Y(site.location))
            long_value = db.session.scalar(ST_X(site.location))

            site_dict = {
                "id": site.id,
                "name": site.name,
                "short_description": site.brief_description,
                "description": site.full_description,
                "city": site.city.name if site.city else None,
                "province": site.city.province.name if site.city and site.city.province else None,
                "country": "AR",
                "lat": float(lat_value) if lat_value else None,
                "long": float(long_value) if long_value else None,
                "tags": [t.slug for t in site.tags],
                "state_of_conservation": (
                    site.conservation_state.state if site.conservation_state else None
                ),
                "inauguration_year": site.inauguration_year,
                "category": site.category.name if site.category else None,
                "inserted_at": site.created_at.isoformat() + "Z" if site.created_at else None,
                "updated_at": site.updated_at.isoformat() + "Z" if site.updated_at else None
            }
            data.append(site_dict)

        # Respuesta según formato del PDF
        return jsonify({
            "data": data,
            "meta": {
                "page": result["current_page"],
                "per_page": result["per_page"],
                "total": result["total"]
            }
        }), 200

    except Exception as e:
        print(f"Error in list_sites: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": {
                "code": "server_error",
                "message": "An unexpected error occurred"
            }
        }), 500


@api_bp.get("/sites/<int:site_id>")
def get_site(site_id):
    """
    GET /sites/{site_id}
    Devuelve el detalle completo de un sitio histórico.
    No requiere autenticación según el PDF.
    """
    try:
        # Usar el servicio para obtener el sitio
        site = historic_site_service.get_historic_site_by_id(site_id)

        # Verificar que esté publicado (visible, validado, no eliminado)
        if not site.is_visible or site.pending_validation or site.deleted_at:
            return jsonify({
                "error": {
                    "code": "not_found",
                    "message": "Site not found"
                }
            }), 404

        # Extraer coordenadas del campo geometry
        lat_value = db.session.scalar(ST_Y(site.location))
        long_value = db.session.scalar(ST_X(site.location))

        # Formatear respuesta según el PDF
        data = {
            "id": site.id,
            "name": site.name,
            "short_description": site.brief_description,
            "description": site.full_description,
            "city": site.city.name if site.city else None,
            "province": site.city.province.name if site.city and site.city.province else None,
            "country": "AR",
            "lat": float(lat_value) if lat_value else None,
            "long": float(long_value) if long_value else None,
            "tags": [t.slug for t in site.tags],
            "state_of_conservation": (
                site.conservation_state.state if site.conservation_state else None
            ),
            "inauguration_year": site.inauguration_year,
            "category": site.category.name if site.category else None,
            "inserted_at": site.created_at.isoformat() + "Z" if site.created_at else None,
            "updated_at": site.updated_at.isoformat() + "Z" if site.updated_at else None
        }

        return jsonify(data), 200

    except ValueError as e:
        # El servicio lanza ValueError cuando no encuentra el sitio
        return jsonify({
            "error": {
                "code": "not_found",
                "message": "Site not found"
            }
        }), 404
    except Exception as e:
        print(f"Error in get_site: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": {
                "code": "server_error",
                "message": "An unexpected error occurred"
            }
        }), 500


@api_bp.post("/sites")
@jwt_required()
def create_site():
    """
    POST /sites
    Crea un nuevo sitio histórico (usuario autenticado).
    Requiere autenticación según el PDF.
    """
    try:
        data = request.get_json() or {}
        user_id = get_jwt_identity()

        # Validar campos requeridos según el PDF
        required_fields = [
            "name", "short_description", "description", "city",
            "province", "country", "lat", "long", "tags", "state_of_conservation", "category", "inauguration_year"
        ]

        missing = [field for field in required_fields if field not in data]

        if missing:
            return jsonify({
                "error": {
                    "code": "invalid_data",
                    "message": "Invalid input data",
                    "details": {field: ["This field is required"] for field in missing}
                }
            }), 400

        # Validar state_of_conservation usando el servicio
        try:
            valid_states = conservation_state_service.get_all_conservation_state()
            valid_state_names = [state.state for state in valid_states]

            if data.get("state_of_conservation") not in valid_state_names:
                return jsonify({
                    "error": {
                        "code": "invalid_data",
                        "message": "Invalid input data",
                        "details": {
                            "state_of_conservation": [
                                f"Must be one of: {', '.join(valid_state_names)}"
                            ]
                        }
                    }
                }), 400

        except Exception as e:
            return jsonify({
                "error": {
                    "code": "server_error",
                    "message": "Error validating conservation state"
                }
            }), 500

        # Validar coordenadas
        if not isinstance(data.get("lat"), (int, float)) or not (-90 <= data["lat"] <= 90):
            return jsonify({
                "error": {
                    "code": "invalid_data",
                    "message": "Invalid input data",
                    "details": {"lat": ["Must be a valid latitude between -90 and 90"]}
                }
            }), 400

        if not isinstance(data.get("long"), (int, float)) or not (-180 <= data["long"] <= 180):
            return jsonify({
                "error": {
                    "code": "invalid_data",
                    "message": "Invalid input data",
                    "details": {"long": ["Must be a valid longitude between -180 and 180"]}
                }
            }), 400

        # Validar que tags sea un array
        if not isinstance(data.get("tags"), list):
            return jsonify({
                "error": {
                    "code": "invalid_data",
                    "message": "Invalid input data",
                    "details": {"tags": ["Must be an array"]}
                }
            }), 400

        # Validar inauguration_year
        inauguration_year = data.get("inauguration_year")
        if inauguration_year is None:
            return jsonify({
                "error": {
                    "code": "invalid_data",
                    "message": "Invalid input data",
                    "details": {"inauguration_year": ["This field is required"]}
                }
            }), 400

        if not isinstance(inauguration_year, int) or not (1500 <= inauguration_year <= 2030):
            return jsonify({
                "error": {
                    "code": "invalid_data",
                    "message": "Invalid input data",
                    "details": {"inauguration_year": ["Must be an integer between 1500 and 2030"]}
                }
            }), 400

        # Buscar o crear provincia y ciudad
        from core.models import Province, City

        province = Province.query.filter(
            db.func.lower(Province.name) == data["province"].lower()
        ).first()

        if not province:
            province = Province(name=data["province"])
            db.session.add(province)
            db.session.flush()

        city = City.query.filter(
            db.func.lower(City.name) == data["city"].lower(),
            City.province_id == province.id
        ).first()

        if not city:
            city = City(name=data["city"], province_id=province.id)
            db.session.add(city)
            db.session.flush()

        # Buscar conservation_state, category (si existe)
        from core.models import ConservationState, Category

        conservation_state = ConservationState.query.filter_by(
            state=data["state_of_conservation"]
        ).first()

        if not conservation_state:
            return jsonify({
                "error": {
                    "code": "invalid_data",
                    "message": "Invalid input data",
                    "details": {"state_of_conservation": ["Invalid conservation state"]}
                }
            }), 400

        # Obtener usuario
        from core.models import User
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                "error": {
                    "code": "unauthorized",
                    "message": "User not found"
                }
            }), 401

        # Buscar tags por slug y convertir a objetos Tag
        from core.models import Tag
        tag_objects = []
        for tag_slug in data["tags"]:
            tag = Tag.query.filter_by(slug=tag_slug).first()
            if tag:
                tag_objects.append(tag)

        # Crear el sitio usando el servicio
        site = historic_site_service.create_historic_site(
            name=data["name"],
            brief_description=data["short_description"],
            full_description=data["description"],
            latitude=data["lat"],
            longitude=data["long"],
            inauguration_year=data.get("inauguration_year", 2000)
        )

        # Asignar relaciones usando el servicio
        # Nota: category puede ser None si no es requerido
        category = Category.query.first()  # Obtener una categoría por defecto o None

        historic_site_service.assign_relations_to_historic_site(
            site,
            conservation_state=conservation_state,
            category=category,
            user=user,
            city=city,
            tags=tag_objects if tag_objects else None
        )

        # Extraer coordenadas para la respuesta
        lat_value = db.session.scalar(ST_Y(site.location))
        long_value = db.session.scalar(ST_X(site.location))

        response_data = {
            "id": site.id,
            "name": site.name,
            "short_description": site.brief_description,
            "description": site.full_description,
            "city": city.name,
            "province": province.name,
            "country": data["country"],
            "lat": float(lat_value) if lat_value else data["lat"],
            "long": float(long_value) if long_value else data["long"],
            "tags": data["tags"],
            "state_of_conservation": data["state_of_conservation"],
            "inauguration_year": site.inauguration_year,
            "category": category.name if site.category else None,
            "inserted_at": site.created_at.isoformat() + "Z" if site.created_at else None,
            "updated_at": site.updated_at.isoformat() + "Z" if site.updated_at else None,
            "user_id": user_id
        }

        return jsonify(response_data), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error in create_site: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": {
                "code": "server_error",
                "message": "An unexpected error occurred"
            }
        }), 500