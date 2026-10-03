import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.database import SessionLocal
from app.services.reminders import send_due_reminders

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def run_reminder_job() -> None:
    with SessionLocal() as db:
        count = send_due_reminders(db)
    logger.info("Reminder job finished: %s email(s) sent", count)


def start_scheduler() -> None:
    if not settings.scheduler_enabled or scheduler.running:
        return
    scheduler.add_job(
        run_reminder_job,
        CronTrigger(hour=settings.reminder_hour, minute=0),
        id="daily_reminders",
        replace_existing=True,
    )
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)