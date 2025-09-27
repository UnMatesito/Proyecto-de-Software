from datetime import datetime, timezone

from core.database import db

historic_site_tag = db.Table(
    "historic_site_tag",
    db.Column(
        "historic_site_id",
        db.Integer,
        db.ForeignKey("historic_site.id"),
        primary_key=True,
    ),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)


class HistoricSite(db.Model):
    __tablename__ = "historic_site"

    # Atributos
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    brief_description = db.Column(db.String, nullable=False)
    full_description = db.Column(db.String, nullable=False)
    latitude = db.Column(db.Double, nullable=False)
    longitude = db.Column(db.Double, nullable=False)
    inauguration_year = db.Column(db.Integer, nullable=False)
    registration_date = db.Column(db.DateTime, nullable=False)
    is_visible = db.Column(db.Boolean, default=False, nullable=False)
    pending_validation = db.Column(db.Boolean, default=True, nullable=False)

    # Timestamps
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    deleted_at = db.Column(db.DateTime, default=None, nullable=True)

    # Relaciones
    city_id = db.Column(db.Integer, db.ForeignKey("city.id"))
    city = db.relationship("City", back_populates="historic_sites")

    conservation_state_id = db.Column(
        db.Integer, db.ForeignKey("conservation_state.id")
    )
    conservation_state = db.relationship(
        "ConservationState", back_populates="historic_sites"
    )

    tags = db.relationship("Tag", secondary=historic_site_tag, back_populates="sites")

    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    category = db.relationship("Category", back_populates="historic_sites")

    proposed_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="historic_sites")

    site_histories = db.relationship("SiteHistory", back_populates="historic_site")

    # Metodos
    def is_deleted(self):
        """Chequea si el sitio historico ha sido eliminado."""
        return self.deleted_at is not None

    def is_active(self):
        """Chequea si el sitio histórico está activo"""
        return self.is_visible is True

    def needs_validation(self):
        """Chequea si el sitio histórico está pendiente de validación"""
        return self.pending_validation is True

    def validate(self):
        """Valida el sitio histórico, marcándolo como visible y no pendiente de validación."""
        self.pending_validation = False
        self.is_visible = True

    def delete_site(self):
        """Marca el sitio histórico como eliminado, estableciendo la fecha de eliminación y haciéndolo no visible."""
        self.deleted_at = datetime.now(timezone.utc)
        self.is_visible = False

    def restore_site(self):
        """Restaura el sitio histórico, eliminando la fecha de eliminación y haciéndolo visible."""
        self.deleted_at = None
        self.is_visible = True

    def get_coordinates(self):
        """Devuelve un diccionario con las coordenadas del sitio histórico."""
        return {"latitude": self.latitude, "longitude": self.longitude}

    def add_tag(self, tag):
        """Agrega una etiqueta al sitio histórico si no está ya presente."""
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag):
        """Elimina una etiqueta del sitio histórico si está presente."""
        if tag in self.tags:
            self.tags.remove(tag)

    def same_city(self, city):
        return city == self.city

    def same_conservation_state(self, state):
        return state == self.conservation_state

    def same_category(self, category):
        return category == self.category

    def same_tags(self, tags):
        return tags == self.tags

    def same_name(self, name):
        return name == self.name

    def same_brief_description(self, brief_description):
        return brief_description == self.brief_description

    def same_full_description(self, full_description):
        return full_description == self.full_description

    def same_latitude(self, latitude):
        return latitude == self.latitude

    def same_longitude(self, longitude):
        return longitude == self.longitude

    def same_inauguration_year(self, inauguration_year):
        return inauguration_year == self.inauguration_year

    def same_registration_date(self, registration_date):
        return registration_date == self.registration_date

    def same_visibility(self, is_visible):
        return is_visible == self.is_visible

    def same_pending_validation(self, pending_validation):
        return pending_validation == self.pending_validation

    def __repr__(self):
        return f"<Historic Site {self.name}>"
