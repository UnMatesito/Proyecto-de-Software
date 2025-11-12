"""
Schemas de validación para la API usando Marshmallow
"""
from .sites_schemas import (
    SiteQuerySchema,
    SiteCreateSchema,
    SiteResponseSchema,
    SiteListResponseSchema,
    HistoricSiteShortSchema
)

from .favorites_schemas import (
    FavoriteQuerySchema
)

from .reviews_schemas import (
    ReviewQuerySchema,
    ReviewResponseSchema,
    ReviewCreateSchema,
    MyReviewResponseSchema
)
__all__ = [
    'SiteQuerySchema',
    'SiteCreateSchema',
    'SiteResponseSchema',
    'SiteListResponseSchema',
    'FavoriteQuerySchema',
    'ReviewQuerySchema',
    'ReviewResponseSchema',
    'ReviewCreateSchema',
    "MyReviewResponseSchema",
    "HistoricSiteShortSchema"
]