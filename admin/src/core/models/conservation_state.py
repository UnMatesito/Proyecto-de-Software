from core.database import db
from datetime import datetime, timezone

class ConservationState(db.Model):
    __tablename__ = "conservation_state"
    id = db.Column(db.Integer, primary_key = True)
    state = db.Column(db.String(50), nullable = False)
    historic_sites = db.relationship("HistoricSite", back_populates = "conservation_state") 
    
    def __repr__(self):
        return f"<Conservation state {self.state}>"