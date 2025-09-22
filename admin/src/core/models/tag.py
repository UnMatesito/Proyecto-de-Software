from datetime import datetime, timezone
from core.database import db
from slugify import slugify

class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column("name", db.String(50), unique = True ,nullable=False)
    slug = db.Column(db.String(50), unique = True, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    deleted_at = db.Column(db.DateTime, default = None)

    sites = db.relationship("HistoricSitee", back_populates="tag")

    def __repr__(self):
        return f"<Tag {self.name}>"
    
    @property
    def name(self):
        return self._name
        
    @name.setter
    def name (self, name):
        self._name = name
        self.slug = slugify(name)

    def has_site():
        return 
    
    def is_deleted(self):
        return self.deleted_at != None
    
    def id_active(self):
        return self.deleted_at == None
