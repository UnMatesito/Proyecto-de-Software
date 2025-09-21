from core.database import db
from datetime import datetime, timezone


class SiteHistory(db.Model):
    __tablename__ = "site_history"

    id = db.Column(db.Integer, primary_key=True)
    historic_site_id = db.Column(db.Integer, db.ForeignKey("historic_site.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    event_type_id = db.Column(db.Integer, db.ForeignKey("event_type.id"), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


    historic_site = db.relationship("HistoricSite", back_populates="site_histories")
    user = db.relationship("User", back_populates="site_histories")
    event_type = db.relationship("EventType", back_populates="site_histories")


    def __repr__(self):
        return f"<SiteHistory {self.id} - {self.historic_site_id} - {self.user_id} - {self.event_type_id}>"