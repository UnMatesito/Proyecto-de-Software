from datetime import datetime, timezone

from core.database import db

issue_label = db.Table(
    "issue_label",
    db.Column("issue_id", db.Integer, db.ForeignKey("issue.id"), primary_key=True),
    db.Column("label_id", db.Integer, db.ForeignKey("label.id"), primary_key=True),
)


class Issue(db.Model):
    __tablename__ = "issue"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="issues")
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
    labels = db.relationship(
        "Label",
        secondary=issue_label,
        backref=db.backref("issues", lazy="dynamic"),
    )

    def __repr__(self):
        return f"<Issue {self.title} - {self.status}>"
