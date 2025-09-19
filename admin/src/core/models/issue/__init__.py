from datetime import datetime, timezone

from core.database import db


class Issue(db.Model):
    __tablename__ = "issue"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="open")

    inserted_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self):
        return f"<Issue {self.title} - {self.status}>"
