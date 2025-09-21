from datetime import datetime, timezone

from slugify import slugify

from core.database import db


class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column("name", db.String(50), nullable=False)
    slug = db.Column(db.String(50), nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self):
        return f"<Tag {self.name}>"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.slug = slugify(value)
