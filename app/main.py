from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import applications, auth


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Temporary: replaced by Alembic migrations later
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Job Application Tracker", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(applications.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}