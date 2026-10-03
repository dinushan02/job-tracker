from collections import Counter
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models import Application, Status, User
from app.schemas import DashboardStats, WeekCount

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

WEEKS = 8


def monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


@router.get("/stats", response_model=DashboardStats)
def stats(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    rows = db.execute(
        select(Application.status, Application.applied_date).where(
            Application.user_id == user.id
        )
    ).all()

    total = len(rows)
    by_status = {s.value: 0 for s in Status}
    for st, _ in rows:
        by_status[st.value] += 1

    # "Response" = anything beyond the initial "applied" status
    responded = total - by_status["applied"]
    response_rate = round(responded / total, 2) if total else 0.0

    this_monday = monday(date.today())
    weeks = [this_monday - timedelta(weeks=i) for i in range(WEEKS - 1, -1, -1)]
    counts = Counter(monday(d) for _, d in rows)
    per_week = [WeekCount(week_start=w, count=counts.get(w, 0)) for w in weeks]

    return DashboardStats(
        total=total,
        by_status=by_status,
        response_rate=response_rate,
        per_week=per_week,
    )