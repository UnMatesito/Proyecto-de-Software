from marshmallow import Schema, fields, validate


class FavoriteQuerySchema(Schema):
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=20, validate=validate.Range(min=1, max=100))
    order_by = fields.Str(load_default="id")
    sorted_by = fields.Str(validate=validate.OneOf(["asc", "desc"]), load_default="asc")
