from core.database import db
from core.models import Feature_flag


def list_feature_flags():
    return Feature_flag.query.all()


def get_feature_flag_by_id():
    return Feature_flag.query.get(feature_flag_id)


def create_feature_flag(**kwargs):
    feature_flag = Feature_flag(**kwargs)
    db.session.add(feature_flag)
    db.session.commit()
    return feature_flag
