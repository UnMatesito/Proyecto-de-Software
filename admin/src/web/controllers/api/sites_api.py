from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.models.historic_site import HistoricSite
from core.models.city import City
from core.models.province import Province
from core.models.tag import Tag
from core.models.category import Category
from core.models.conservation_state import ConservationState
from core.models.user import User
from core.database import db
from sqlalchemy import func, or_, text
from geoalchemy2.functions import ST_SetSRID, ST_MakePoint, ST_DWithin, ST_X, ST_Y
from . import api_bp


@api_bp.get("/sites")
def list_sites():
    """
    GET /sites
    Lista sitios históricos con filtros combinables según la especificación de la API.

    Parámetros:
      - name, description: búsqueda parcial (case-insensitive)
      - city, province: exactos (case-insensitive)
      - tags: separados por coma
      - order_by: latest | oldest | rating-5-1 | rating-1-5
      - lat, long, radius: búsqueda geoespacial
      - page, per_page: paginación

    Respuesta según según la especificación de la API:
      - "data": lista de sitios
      - "meta": {page, per_page, total}
    """
    try:
        # Parámetros de búsqueda
        name = request.args.get("name")
        description = request.args.get("description")
        city_name = request.args.get("city")
        province_name = request.args.get("province")
        tags_str = request.args.get("tags")
        order_by = request.args.get("order_by", "latest")

        # Parámetros geoespaciales
        lat = request.args.get("lat", type=float)
        lon = request.args.get("long", type=float)
        radius = request.args.get("radius", type=float)

        # Parámetros de paginación
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        # Validaciones
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

        # Construir query base (solo sitios visibles y validados)
        query = HistoricSite.query.filter(
            HistoricSite.is_visible.is_(True),
            HistoricSite.pending_validation.is_(False)
        )

        # Filtro por nombre (búsqueda parcial, case-insensitive)
        if name:
            query = query.filter(HistoricSite.name.ilike(f"%{name}%"))

        # Filtro por descripción (búsqueda parcial, case-insensitive)
        if description:
            query = query.filter(
                or_(
                    HistoricSite.brief_description.ilike(f"%{description}%"),
                    HistoricSite.full_description.ilike(f"%{description}%")
                )
            )

        # Filtro por ciudad (búsqueda exacta, case-insensitive)
        if city_name:
            query = query.join(City).filter(func.lower(City.name) == city_name.lower())

        # Filtro por provincia (búsqueda exacta, case-insensitive)
        if province_name:
            if not city_name:  # Si no se filtró por ciudad, hacer el join
                query = query.join(City)
            query = query.join(Province).filter(func.lower(Province.name) == province_name.lower())

        # Filtro por tags (búsqueda por múltiples tags)
        if tags_str:
            tag_list = [t.strip() for t in tags_str.split(",") if t.strip()]
            if tag_list:
                # Buscar sitios que tengan al menos uno de los tags
                # Usar el slug del tag para la búsqueda
                query = query.join(HistoricSite.tags).filter(Tag.slug.in_(tag_list))

        # Filtro geoespacial (si se pasan lat, long y radius)
        if lat is not None and lon is not None and radius is not None:
            # Crear punto geográfico con ST_MakePoint(longitud, latitud)
            point = ST_SetSRID(ST_MakePoint(lon, lat), 4326)
            # Filtrar por distancia (radius en km, convertir a metros)
            query = query.filter(
                ST_DWithin(HistoricSite.location, point, radius * 1000)
            )

        # Ordenamiento
        if order_by == "latest":
            query = query.order_by(HistoricSite.created_at.desc())
        elif order_by == "oldest":
            query = query.order_by(HistoricSite.created_at.asc())
        elif order_by in ["rating-5-1", "rating-1-5"]:
            # Calcular rating promedio mediante subquery
            from core.models.review import Review

            # Subquery para calcular el promedio de ratings
            avg_rating = db.session.query(
                Review.historic_site_id,
                func.avg(Review.rating).label('avg_rating')
            ).filter(
                Review.status == 'approved'  # Solo contar reviews aprobadas
            ).group_by(Review.historic_site_id).subquery()

            # Join con la subquery
            query = query.outerjoin(
                avg_rating,
                HistoricSite.id == avg_rating.c.historic_site_id
            )

            if order_by == "rating-5-1":
                # Ordenar de mayor a menor (5 a 1)
                query = query.order_by(avg_rating.c.avg_rating.desc().nullslast())
            else:  # rating-1-5
                # Ordenar de menor a mayor (1 a 5)
                query = query.order_by(avg_rating.c.avg_rating.asc().nullslast())

        # Ejecutar paginación
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        sites = pagination.items

        # Formatear respuesta según la especificación de la API
        data = []
        for s in sites:
            # Extraer coordenadas del campo geometry
            lat_value = db.session.scalar(ST_Y(s.location))
            long_value = db.session.scalar(ST_X(s.location))

            site_dict = {
                "id": s.id,
                "name": s.name,
                "short_description": s.brief_description,
                "description": s.full_description,
                "city": s.city.name if s.city else None,
                "province": s.city.province.name if s.city and s.city.province else None,
                "country": "AR",  # Según la especificación de la API, siempre es "AR"
                "lat": float(lat_value) if lat_value else None,
                "long": float(long_value) if long_value else None,
                "tags": [t.slug for t in s.tags],  # Usar slug según el esquema
                "state_of_conservation": (
                    s.conservation_state.state if s.conservation_state else None
                ),
                "inserted_at": s.created_at.isoformat() + "Z" if s.created_at else None,
                "updated_at": s.updated_at.isoformat() + "Z" if s.updated_at else None
            }
            data.append(site_dict)

        # Respuesta según formato de la especificación de la API
        return jsonify({
            "data": data,
            "meta": {
                "page": pagination.page,
                "per_page": per_page,
                "total": pagination.total
            }
        }), 200

    except Exception as e:
        print(f"Error in list_sites: {str(e)}")  # Para debugging
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
    No requiere autenticación según la especificación de la API.
    """
    try:
        site = HistoricSite.query.get(site_id)

        if not site:
            return jsonify({
                "error": {
                    "code": "not_found",
                    "message": "Site not found"
                }
            }), 404

        # Extraer coordenadas del campo geometry
        lat_value = db.session.scalar(ST_Y(site.location))
        long_value = db.session.scalar(ST_X(site.location))

        # Formatear respuesta según la especificación de la API
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
            "inserted_at": site.created_at.isoformat() + "Z" if site.created_at else None,
            "updated_at": site.updated_at.isoformat() + "Z" if site.updated_at else None
        }

        return jsonify(data), 200

    except Exception as e:
        print(f"Error in get_site: {str(e)}")  # Para debugging
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
    Requiere autenticación según la especificación de la API.
    """
    try:
        data = request.get_json() or {}
        user_id = get_jwt_identity()

        # Validar campos requeridos según la especificación de la API
        required_fields = [
            "name", "short_description", "description", "city",
            "province", "country", "lat", "long", "tags", "state_of_conservation"
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

        # Validar state_of_conservation
        valid_states = ["excelente", "bueno", "regular", "malo"]
        if data.get("state_of_conservation") not in valid_states:
            return jsonify({
                "error": {
                    "code": "invalid_data",
                    "message": "Invalid input data",
                    "details": {
                        "state_of_conservation": [
                            f"Must be one of: {', '.join(valid_states)}"
                        ]
                    }
                }
            }), 400

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

        # Buscar o crear provincia
        province = Province.query.filter(
            func.lower(Province.name) == data["province"].lower()
        ).first()

        if not province:
            province = Province(name=data["province"])
            db.session.add(province)
            db.session.flush()

        # Buscar o crear ciudad
        city = City.query.filter(
            func.lower(City.name) == data["city"].lower(),
            City.province_id == province.id
        ).first()

        if not city:
            city = City(name=data["city"], province_id=province.id)
            db.session.add(city)
            db.session.flush()

        # Buscar conservation_state
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

        # Crear el punto geográfico usando PostGIS
        # ST_MakePoint(longitud, latitud)
        location_wkt = f"SRID=4326;POINT({data['long']} {data['lat']})"

        # Crear el sitio histórico
        site = HistoricSite(
            name=data["name"],
            brief_description=data["short_description"],
            full_description=data["description"],
            inauguration_year=data.get("inauguration_year", 2000),  # Valor por defecto si no se proporciona
            is_visible=True,  # Por defecto visible
            pending_validation=True,  # Por defecto pendiente de validación
            city_id=city.id,
            conservation_state_id=conservation_state.id,
            proposed_by=user_id,
            location=location_wkt
        )

        db.session.add(site)
        db.session.flush()  # Para obtener el ID

        # Agregar tags
        if data["tags"]:
            for tag_slug in data["tags"]:
                # Buscar tag por slug
                tag = Tag.query.filter_by(slug=tag_slug).first()
                if tag:
                    site.tags.append(tag)

        db.session.commit()

        # Extraer coordenadas para la respuesta
        lat_value = db.session.scalar(ST_Y(site.location))
        long_value = db.session.scalar(ST_X(site.location))

        # Respuesta según la especificación de la API
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
            "inserted_at": site.created_at.isoformat() + "Z" if site.created_at else None,
            "updated_at": site.updated_at.isoformat() + "Z" if site.updated_at else None,
            "user_id": user_id
        }

        return jsonify(response_data), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error in create_site: {str(e)}")  # Para debugging
        return jsonify({
            "error": {
                "code": "server_error",
                "message": "An unexpected error occurred"
            }
        }), 500