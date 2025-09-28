from datetime import datetime, timezone

from core.database import db


class SiteHistory(db.Model):
    __tablename__ = "site_history"

    # Atributos
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relaciones
    historic_site_id = db.Column(
        db.Integer,
        db.ForeignKey("historic_site.id", ondelete="CASCADE"),
        nullable=False,
    )
    historic_site = db.relationship("HistoricSite", back_populates="site_histories")

    event_type_id = db.Column(
        db.Integer, db.ForeignKey("event_type.id", ondelete="CASCADE"), nullable=False
    )
    event_type = db.relationship("EventType", back_populates="site_histories")

    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    user = db.relationship("User", back_populates="site_histories")

    # Metodos
    def __repr__(self):
        return f"<SiteHistory {self.id} - {self.historic_site_id} - {self.user_id} - {self.event_type_id}>"

    @classmethod
    def log_event(cls, historic_site_id, user_id, event_type_id, description):
        """Crea un nuevo registro de historial de sitio."""
        site_history = cls(
            historic_site_id=historic_site_id,
            user_id=user_id,
            event_type_id=event_type_id,
            description=description,
        )
        db.session.add(site_history)
        db.session.commit()
        return site_history
