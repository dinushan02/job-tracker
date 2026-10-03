from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models import User
from app.services.reminders import send_due_reminders

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.post("/run")
def run_my_reminders(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return {"emails_sent": send_due_reminders(db, user_id=user.id)}