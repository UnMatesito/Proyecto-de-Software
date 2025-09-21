from core.database import db
from core.models import Label


def create_label(name):
    label = Label(name=name)
    db.session.add(label)
    db.session.commit()
    return label
