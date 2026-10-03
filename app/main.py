import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import applications, auth, dashboard, reminders
from app.tasks.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Temporary: replaced by Alembic migrations later
    Base.metadata.create_all(bind=engine)
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="Job Application Tracker", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(applications.router)
app.include_router(dashboard.router)
app.include_router(reminders.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}