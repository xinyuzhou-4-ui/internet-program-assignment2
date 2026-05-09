from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from auth_user import get_current_user
from database import get_session
from models import User, UserActivity


router = APIRouter()


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only.")
    return current_user


@router.get("/admin/activities", response_model=List[UserActivity])
def get_activities(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user),
):
    statement = select(UserActivity).order_by(UserActivity.created_at.desc())
    return session.exec(statement).all()
