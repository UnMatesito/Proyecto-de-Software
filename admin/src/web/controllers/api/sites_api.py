from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError
from geoalchemy2.functions import ST_X, ST_Y
from marshmallow import ValidationError

from core.database import db
from core.services import historic_site_service
from web.schemas import SiteCreateSchema, SiteQuerySchema
from web.utils.format_marshmallow_validation_errors import format_validation_errors

from . import api_bp


def _serialize_site(site):
    """Serializa un sitio histórico para la respuesta pública de la API."""

    lat_value = db.session.scalar(ST_Y(site.location))
    lon_value = db.session.scalar(ST_X(site.location))

    images = [
        {
            "id": image.id,
            "url": image.public_url,
            "title": image.title,
            "description": image.description,
            "is_cover": image.is_cover,
            "order": image.order if image.order is not None else 0,
        }
        for image in sorted(
            site.images,
            key=lambda img: (
                img.order if img.order is not None else 0,
                img.id,
            ),
        )
    ]

    return {
        "id": site.id,
        "name": site.name,
        "short_description": site.brief_description,
        "description": site.full_description,
        "review_count": site.rating_count,
        "average_rating": site.average_rating,
        "city": site.city.name if site.city else None,
        "province": site.city.province.name if site.city and site.city.province else None,
        "lat": float(lat_value) if lat_value is not None else None,
        "lon": float(lon_value) if lon_value is not None else None,
        "tags": [t.slug for t in site.tags],
        "state_of_conservation": (
            site.conservation_state.state if site.conservation_state else None
        ),
        "inauguration_year": site.inauguration_year,
        "category": site.category.name if site.category else None,
        "inserted_at": site.created_at.isoformat() + "Z" if site.created_at else None,
        "updated_at": site.updated_at.isoformat() + "Z" if site.updated_at else None,
        "images": images,
    }


@api_bp.get("/sites")
def list_sites():
    """
    GET /sites
    Lista sitios históricos con filtros combinables según la especificación de la API.
    """
    try:
        # Validar parámetros con schema
        schema = SiteQuerySchema()
        try:
            params = schema.load(request.args)
        except ValidationError as err:
            return jsonify({
                "error": {
                    "code": "invalid_query",
                    "message": "Parameter validation failed",
                    "details": err.messages,
                }
            }), 400

        favorites_only = params.get("favorites", False)
        user_id = None

        if favorites_only:
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()
            except NoAuthorizationError:
                return jsonify({
                    "error": {
                        "code": "authorization_required",
                        "message": "Authentication is required to filter by favorites",
                    }
                }), 401

            if not user_id:
                return jsonify({
                    "error": {
                        "code": "authorization_required",
                        "message": "Authentication is required to filter by favorites",
                    }
                }), 401

        # Delegar al servicio con todos los filtros combinables
        result = historic_site_service.list_published_sites(
            name=params.get("name"),
            description=params.get("description"),
            city_name=params.get("city"),
            province_name=params.get("province"),
            tags_str=params.get("tags"),
            order_by=params.get("order_by", "latest"),
            lat=params.get("lat"),
            lon=params.get("lon"),
            radius=params.get("radius"),
            favorited_by_user_id=user_id if favorites_only else None,
            page=params.get("page", 1),
            per_page=params.get("per_page", 20),
        )

        # Formatear respuesta de salida
        data = [_serialize_site(site) for site in result["items"]]

        return jsonify({
            "data": data,
            "meta": {
                "page": result["current_page"],
                "per_page": result["per_page"],
                "total": result["total"],
                "total_pages": result["pages"],
            },
        }), 200

    except Exception as e:
        print(f"Error in list_sites: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({
            "error": {
                "code": "server_error",
                "message": "An unexpected error occurred",
            }
        }), 500


@api_bp.get("/sites/<int:site_id>")
def get_site(site_id):
    """
    GET /sites/{site_id}
    Devuelve el detalle completo de un sitio histórico.
    """
    try:
        site = historic_site_service.get_published_site_by_id(site_id)
        return jsonify(_serialize_site(site)), 200

    except ValueError:
        return jsonify({
            "error": {
                "code": "not_found",
                "message": "Site not found",
            }
        }), 404
    except Exception as e:
        print(f"Error in get_site: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({
            "error": {
                "code": "server_error",
                "message": "An unexpected error occurred",
            }
        }), 500


@api_bp.post("/sites")
@jwt_required()
def create_site():
    """
    POST /sites
    Crea un nuevo sitio histórico (usuario autenticado).
    """
    try:
        data = request.get_json() or {}
        user_id = get_jwt_identity()

        # Validar datos con schema
        schema = SiteCreateSchema()
        try:
            validated_data = schema.load(data)
        except ValidationError as err:
            return jsonify(format_validation_errors(err.messages)), 400

        # Delegar creación al servicio
        site = historic_site_service.create_site_from_api(
            user_id=user_id,
            name=validated_data["name"],
            short_description=validated_data["short_description"],
            description=validated_data["description"],
            city_name=validated_data["city"],
            province_name=validated_data["province"],
            lat=validated_data["lat"],
            lon=validated_data["lon"],
            tags=validated_data["tags"],
            state_of_conservation=validated_data["state_of_conservation"],
            inauguration_year=validated_data["inauguration_year"],
            category_name=validated_data.get("category"),
        )

        response_data = _serialize_site(site)
        response_data["user_id"] = user_id

        return jsonify(response_data), 201

    except ValueError as e:
        return jsonify({
            "error": {
                "code": "invalid_data",
                "message": "Invalid input data",
                "details": {"error": [str(e)]},
            }
        }), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error in create_site: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({
            "error": {
                "code": "server_error",
                "message": "An unexpected error occurred",
            }
        }), 500