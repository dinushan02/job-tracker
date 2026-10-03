from collections import defaultdict
from datetime import date
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Application, Status, User
from app.services.email import send_email


def send_due_reminders(
    db: Session,
    send: Callable[[str, str, str], None] | None = None,
    today: date | None = None,
    user_id: int | None = None,
) -> int:
    """Email each user their applications due for follow-up today.

    Returns the number of emails sent (one per user).
    """
    send = send or send_email
    today = today or date.today()

    stmt = (
        select(Application, User)
        .join(User, Application.user_id == User.id)
        .where(Application.follow_up_date == today)
        .where(Application.status.in_([Status.applied, Status.interview]))
        .order_by(Application.company)
    )
    if user_id is not None:
        stmt = stmt.where(Application.user_id == user_id)

    by_email: dict[str, list[Application]] = defaultdict(list)
    for application, user in db.execute(stmt).all():
        by_email[user.email].append(application)

    for email, apps in by_email.items():
        lines = [f"- {a.company}: {a.role} ({a.status.value})" for a in apps]
        body = "Time to follow up on these applications today:\n\n" + "\n".join(lines)
        send(email, f"Follow-up reminder: {len(apps)} application(s) due today", body)

    return len(by_email)