from core.database import db
from core.models.tag import Tag


def create_tag(name: str) -> Tag:
    tag = Tag(name=name)
    db.session.add(tag)
    db.session.commit()
    return tag
