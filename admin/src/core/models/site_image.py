from datetime import datetime, timezone

from core.database import db


class SiteImage(db.Model):
    __tablename__ = "site_image"

    # Atributos
    id = db.Column(db.Integer, primary_key=True)
    public_url = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    is_cover = db.Column(db.Boolean, default=False, nullable=False)
    order = db.Column(db.Integer, nullable=True, default=0)

    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)

    # Relaciones
    historic_site_id = db.Column(db.Integer, db.ForeignKey("historic_site.id", ondelete="CASCADE"), nullable=False)
    historic_site = db.relationship("HistoricSite", back_populates="images")

    # Metodos
    def __repr__(self):
        return f"<SiteImage {self.title}>"