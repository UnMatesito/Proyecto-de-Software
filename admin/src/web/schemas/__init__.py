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
    'HistoricSiteShortSchema',
    'ReviewQuerySchema',
    'ReviewResponseSchema',
    'ReviewCreateSchema',
    'MyReviewResponseSchema'
]