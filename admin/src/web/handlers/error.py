from dataclasses import dataclass

from flask import render_template


@dataclass
class HTTPError:
    code: int
    message: str
    description: str


def not_found(e):
    """Manejador para error 404 - Not Found"""
    error = HTTPError(
        code=404,
        message="Página no encontrada",
        description="La página que buscas no existe.",
    )

    return render_template("error.html", error=error), 404


def internal_server_error(e):
    """Manejador para error 500 - Internal Server Error"""
    error = HTTPError(
        code=500,
        message="Error interno del servidor",
        description="Ha ocurrido un error inesperado en el servidor.",
    )
    return render_template("error.html", error=error), 500


def unauthorized(e):
    """Manejador para error 401 - Unauthorized"""
    error = HTTPError(
        code=401,
        message="No autorizado",
        description="No tienes una sesión iniciada para poder acceder a este recurso.",
    )
    return render_template("error.html", error=error), 401


def forbidden(e):
    """Manejador para error 403 - Forbidden"""
    error = HTTPError(
        code=403,
        message="Sin permisos",
        description="No tienes los permisos necesarios para acceder a este recurso.",
    )
    return render_template("error.html", error=error), 403
