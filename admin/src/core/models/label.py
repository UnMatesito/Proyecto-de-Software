from core.database import db

class Label(db.Model):
    __tablename__ = "label"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f"<Label {self.name}>"
