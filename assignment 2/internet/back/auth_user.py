import os
from datetime import datetime, timedelta
from typing import List, Optional

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import func
from sqlmodel import SQLModel, Session, select

from database import get_session
from models import User, UserActivity

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = os.getenv("SECRET_KEY", "expense_tracker_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRegister(SQLModel):
    username: str
    email: str
    password: str


class UserRead(SQLModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime


class UserAdminRead(SQLModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime


class UserAdminUpdate(SQLModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None


class LoginUserRead(SQLModel):
    id: int
    username: str
    email: str
    role: str


class LoginResponse(SQLModel):
    access_token: str
    token_type: str
    user: LoginUserRead


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return password_context.verify(plain_password, hashed_password)
    except ValueError:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )


def create_access_token(user_id: int, email: str, role: str) -> str:
    expire_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": expire_time,
    }
    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)


async def db_get_user_by_email(session: Session, email: str) -> Optional[User]:
    normalized_email = email.strip().lower()
    statement = select(User).where(func.lower(User.email) == normalized_email)
    return session.exec(statement).first()


async def db_get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    return session.get(User, user_id)


async def db_create_user(
    session: Session, username: str, email: str, password: str
) -> User:
    user = User(
        username=username.strip(),
        email=email.strip().lower(),
        hashed_password=hash_password(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


async def create_activity_log(
    session: Session, user_id: int, action: str, detail: Optional[str] = None
) -> UserActivity:
    activity = UserActivity(user_id=user_id, action=action, detail=detail)
    session.add(activity)
    session.commit()
    session.refresh(activity)
    return activity


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        email = payload.get("email")
        role = payload.get("role")

        if user_id is None or email is None or role is None:
            raise HTTPException(status_code=401, detail="Unauthorized.")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Unauthorized.")

    user = await db_get_user_by_id(session, int(user_id))

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized.")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account is inactive.")

    return user


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden.")
    return current_user


@router.post("/register", response_model=UserRead)
async def register(user_data: UserRegister, session: Session = Depends(get_session)):
    email = user_data.email.strip().lower()
    existing_user = await db_get_user_by_email(session, email)

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists.")

    return await db_create_user(
        session=session,
        username=user_data.username,
        email=email,
        password=user_data.password,
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    email = form_data.username.strip().lower()
    user = await db_get_user_by_email(session, email)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="This account is inactive.")

    await create_activity_log(session, user.id, "login", "User logged in.")

    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        },
    }


@router.post("/logout")
async def logout(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    await create_activity_log(session, current_user.id, "logout", "User logged out.")
    return {"message": "Logout recorded."}


@router.get("/admin/activities", response_model=List[UserActivity])
async def get_all_activities(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user),
):
    statement = select(UserActivity).order_by(UserActivity.created_at.desc())
    return session.exec(statement).all()


@router.get("/admin/users", response_model=List[UserAdminRead])
async def get_all_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user),
):
    statement = select(User).order_by(User.id)
    return session.exec(statement).all()


@router.put("/admin/users/{user_id}", response_model=UserAdminRead)
async def update_user(
    user_id: int,
    user_data: UserAdminUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user),
):
    user = await db_get_user_by_id(session, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if user_data.role is not None:
        if user_data.role not in ["user", "admin"]:
            raise HTTPException(
                status_code=400, detail="Role must be 'user' or 'admin'."
            )
        user.role = user_data.role

    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    session.add(user)
    session.commit()
    session.refresh(user)

    await create_activity_log(
        session,
        current_user.id,
        "update_user",
        f"Updated user {user.id}: role={user.role}, is_active={user.is_active}",
    )

    return user


@router.delete("/admin/users/{user_id}", response_model=UserAdminRead)
async def deactivate_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user),
):
    user = await db_get_user_by_id(session, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.is_active = False
    session.add(user)
    session.commit()
    session.refresh(user)

    await create_activity_log(
        session,
        current_user.id,
        "deactivate_user",
        f"Deactivated user {user.id}: {user.email}",
    )

    return user
