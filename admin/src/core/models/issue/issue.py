from core.database import db
from core.models import Issue


def list_issues():
    return Issue.query.all()


def get_issue_by_id(issue_id):
    return Issue.query.get(issue_id)


def create_issue(email, title, description, status="open"):
    issue = Issue(email=email, title=title, description=description, status=status)
    db.session.add(issue)
    db.session.commit()
    return issue
