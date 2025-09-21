from core.database import db
from core.models import Issue, Label


def list_issues():
    return Issue.query.all()


def get_issue_by_id(issue_id):
    return Issue.query.get(issue_id)


def create_issue(email, title, description, status="open"):
    issue = Issue(email=email, title=title, description=description, status=status)
    db.session.add(issue)
    db.session.commit()
    return issue

def assign_issue_to_user(issue_id, user_id):
    issue = get_issue_by_id(issue_id)
    if issue:
        issue.user_id = user_id
        db.session.commit()
    return issue


def assign_labels_to_issue(issue_id, label_ids):
    issue = get_issue_by_id(issue_id)
    if issue:
        labels = db.session.query(Label).filter(Label.id.in_(label_ids)).all()
        issue.labels = labels
        db.session.commit()
    return issue


def assign_issue(issue, user):
    issue.user = user
    db.session.commit()
    return issue

def assign_labels(issue, labels):
    issue.labels = labels
    db.session.commit()
    return issue