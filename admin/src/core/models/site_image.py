from datetime import datetime, timezone

from core.database import db


class SiteImage(db.Model):
    __tablename__ = "site_image"

    # Atributos
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)

    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)

    # Relaciones
    historic_site_id = db.Column(db.Integer, db.ForeignKey("historic_site.id", ondelete="CASCADE"))
    historic_site = db.relationship("HistoricSite", back_populates="images")

    # Metodos
    def __repr__(self):
        return f"<SiteImage {self.id} - {self.filename}>"