from core.database import db
from datetime import datetime, timezone

class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    slug = db.Column(db.String(50), nullable = False)
    created_a = db.Column(
        db.DateTime, 
        default = lambda: datetime.now(timezone),
        nullable = False)   
            
    def __repr__(self):
        return f"<Tag {self.name}>"