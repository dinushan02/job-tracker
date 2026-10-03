from pydantic import BaseModel, ConfigDict, EmailStr, Field

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import Status


class ApplicationBase(BaseModel):
    company: str = Field(min_length=1, max_length=120)
    role: str = Field(min_length=1, max_length=120)
    status: Status = Status.applied
    applied_date: date = Field(default_factory=date.today)
    follow_up_date: date | None = None
    notes: str | None = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    company: str | None = Field(default=None, min_length=1, max_length=120)
    role: str | None = Field(default=None, min_length=1, max_length=120)
    status: Status | None = None
    applied_date: date | None = None
    follow_up_date: date | None = None
    notes: str | None = None


class ApplicationOut(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class WeekCount(BaseModel):
    week_start: date
    count: int


class DashboardStats(BaseModel):
    total: int
    by_status: dict[str, int]
    response_rate: float
    per_week: list[WeekCount]
