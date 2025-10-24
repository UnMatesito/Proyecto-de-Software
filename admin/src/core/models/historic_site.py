from datetime import datetime, timezone

from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape

from core.database import db

historic_site_tag = db.Table(
    "historic_site_tag",
    db.Column(
        "historic_site_id",
        db.Integer,
        db.ForeignKey("historic_site.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "tag_id",
        db.Integer,
        db.ForeignKey("tag.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

user_favorite_site = db.Table(
    "user_favorite_site",
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "historic_site_id",
        db.Integer,
        db.ForeignKey("historic_site.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

class HistoricSite(db.Model):
    __tablename__ = "historic_site"

    # Atributos
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    brief_description = db.Column(db.String(50), nullable=False)
    full_description = db.Column(db.String, nullable=False)
    inauguration_year = db.Column(db.Integer, nullable=False)
    is_visible = db.Column(db.Boolean, default=False, nullable=False)
    pending_validation = db.Column(db.Boolean, default=True, nullable=False)
    location = db.Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    # TODO: VER QUÉ HACER CON EL PAIS

    # Latitud
    @property
    def latitude(self) -> float:
        if self.location:
            punto = to_shape(self.location)
            return punto.y
        return None

    # Longitud
    @property
    def longitude(self) -> float:
        if self.location:
            punto = to_shape(self.location)
            return punto.x
        return None

    # Timestamps
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    deleted_at = db.Column(db.DateTime, default=None, nullable=True)

    # Relaciones
    city_id = db.Column(db.Integer, db.ForeignKey("city.id", ondelete="CASCADE"))
    city = db.relationship("City", back_populates="historic_sites")

    conservation_state_id = db.Column(
        db.Integer, db.ForeignKey("conservation_state.id", ondelete="CASCADE")
    )
    conservation_state = db.relationship(
        "ConservationState", back_populates="historic_sites"
    )

    tags = db.relationship("Tag", secondary=historic_site_tag, back_populates="sites")

    category_id = db.Column(
        db.Integer, db.ForeignKey("category.id", ondelete="CASCADE")
    )
    category = db.relationship("Category", back_populates="historic_sites")

    proposed_by = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))
    user = db.relationship("User", back_populates="historic_sites")

    site_histories = db.relationship(
        "SiteHistory", back_populates="historic_site", cascade="all, delete-orphan"
    )

    images = db.relationship("SiteImage", back_populates="historic_site", cascade="all, delete-orphan")

    favorited_by = db.relationship(
        "User",
        secondary="user_favorite_site",
        back_populates="favorite_sites",
    )

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
        """Restaura el sitio histórico, eliminando la fecha de eliminación, haciéndolo no visible y en estado de validacion."""

        self.deleted_at = None
        self.is_visible = False
        self.pending_validation = True
        return self

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
        """Retorna verdadero o falso si el sitio histórico posee la misma ciuedad"""

        return city == self.city

    def same_conservation_state(self, state):
        """Retorna verdadero o falso si el sitio histórico posee el mismo estado de conservación"""

        return state == self.conservation_state

    def same_category(self, category):
        """Retorna verdadero o falso si el sitio histórico posee la misma categoria"""

        return category == self.category

    def same_tags(self, tags):
        """Retorna verdadero o falso si el sitio histórico posee los mismos tags"""

        return tags == self.tags

    def same_name(self, name):
        """Retorna verdadero o falso si el sitio histórico posee el mismo nombre"""

        return name == self.name

    def same_brief_description(self, brief_description):
        """Retorna verdadero o falso si el sitio histórico posee la misma descripción breve"""

        return brief_description == self.brief_description

    def same_full_description(self, full_description):
        """Retorna verdadero o falso si el sitio histórico posee la descripción completa"""

        return full_description == self.full_description

    def same_latitude(self, latitude):
        """Retorna verdadero o falso si el sitio histórico posee la misma latitud"""

        return latitude == self.latitude

    def same_longitude(self, longitude):
        """Retorna verdadero o falso si el sitio histórico posee la misma longitud"""

        return longitude == self.longitude

    def same_inauguration_year(self, inauguration_year):
        """Retorna verdadero o falso si el sitio histórico posee el mismo año de inaguración"""

        return inauguration_year == self.inauguration_year

    def same_visibility(self, is_visible):
        """Retorna verdadero o falso si el sitio histórico posee el mismo estado de visibilidad"""

        return is_visible == self.is_visible

    def same_pending_validation(self, pending_validation):
        """Retorna verdadero o falso si el sitio histórico posee el mismo estado de validación pendiente"""

        return pending_validation == self.pending_validation

    def get_cover_image(self):
        """Retorna la imagen de portada del sitio histórico si existe, de lo contrario retorna None"""

        for image in self.images:
            if image.is_cover:
                return image
        return None

    def get_image_urls(self):
        """Retorna una lista de URLs de las imágenes asociadas al sitio histórico."""

        return [image.public_url for image in self.images]

    def __repr__(self):
        """Retorna una representación de sitio histórico la cual posee su nombre"""

        return f"<Historic Site {self.name}>"
