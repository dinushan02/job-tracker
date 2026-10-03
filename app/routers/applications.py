from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Application, Status
from app.schemas import ApplicationCreate, ApplicationOut, ApplicationUpdate

router = APIRouter(prefix="/applications", tags=["applications"])


def get_or_404(db: Session, app_id: int) -> Application:
    obj = db.get(Application, app_id)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found")
    return obj


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    obj = Application(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("", response_model=list[ApplicationOut])
def list_applications(
    status_filter: Status | None = Query(None, alias="status"),
    q: str | None = Query(None, description="Search company or role"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    stmt = select(Application).order_by(Application.created_at.desc())
    if status_filter:
        stmt = stmt.where(Application.status == status_filter)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(Application.company.ilike(like), Application.role.ilike(like))
        )
    return db.scalars(stmt.offset(skip).limit(limit)).all()


@router.get("/{app_id}", response_model=ApplicationOut)
def read_application(app_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, app_id)


@router.put("/{app_id}", response_model=ApplicationOut)
def update_application(
    app_id: int, payload: ApplicationUpdate, db: Session = Depends(get_db)
):
    obj = get_or_404(db, app_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(app_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, app_id))
    db.commit()
