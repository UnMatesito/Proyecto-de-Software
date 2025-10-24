"""
Schemas de validación para la API usando Marshmallow
"""
from .sites_schemas import (
    SiteQuerySchema,
    SiteCreateSchema,
    SiteResponseSchema,
    SiteListResponseSchema,
    format_validation_errors
)

from .favorites_schemas import (
    FavoriteQuerySchema,
)
__all__ = [
    'SiteQuerySchema',
    'SiteCreateSchema',
    'SiteResponseSchema',
    'SiteListResponseSchema',
    'format_validation_errors',
    'FavoriteQuerySchema',
]