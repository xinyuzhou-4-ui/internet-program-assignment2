from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, SQLModel, select

from auth_user import create_activity_log, get_current_user
from database import get_session
from models import User, UserActivity


router = APIRouter()


class AdminUserRead(SQLModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool


class AdminUserUpdate(SQLModel):
    role: str | None = None
    is_active: bool | None = None


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


@router.get("/admin/users", response_model=List[AdminUserRead])
def get_all_users(
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_admin_user),
):
    statement = select(User).order_by(User.id)
    return session.exec(statement).all()


@router.put("/admin/users/{user_id}", response_model=AdminUserRead)
def update_user(
    user_id: int,
    user_update: AdminUserUpdate,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_admin_user),
):
    target_user = session.get(User, user_id)
    if target_user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    if user_update.role is not None:
        if user_update.role not in ["user", "admin"]:
            raise HTTPException(status_code=400, detail="Role must be user or admin.")
        target_user.role = user_update.role

    if user_update.is_active is not None:
        target_user.is_active = user_update.is_active

    session.add(target_user)
    session.commit()
    session.refresh(target_user)

    create_activity_log(
        session,
        admin_user.id,
        "update_user",
        f"Updated user id {target_user.id}",
    )
    session.refresh(target_user)
    return target_user


@router.delete("/admin/users/{user_id}", response_model=AdminUserRead)
def deactivate_user(
    user_id: int,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_admin_user),
):
    target_user = session.get(User, user_id)
    if target_user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    target_user.is_active = False
    session.add(target_user)
    session.commit()
    session.refresh(target_user)

    create_activity_log(
        session,
        admin_user.id,
        "deactivate_user",
        f"Deactivated user id {target_user.id}",
    )
    session.refresh(target_user)
    return target_user
