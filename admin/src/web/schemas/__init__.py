"""
Schemas de validación para la API usando Marshmallow
"""
from .favorites_schemas import FavoriteQuerySchema
from .reviews_schemas import (
    MyReviewQuerySchema,
    MyReviewResponseSchema,
    ReviewCreateSchema,
    ReviewQuerySchema,
    ReviewResponseSchema,
)
from .sites_schemas import (
    HistoricSiteShortSchema,
    SiteCreateSchema,
    SiteListResponseSchema,
    SiteQuerySchema,
    SiteResponseSchema,
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
    "MyReviewQuerySchema",
    "MyReviewResponseSchema",
    "HistoricSiteShortSchema"
]