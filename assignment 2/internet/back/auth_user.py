import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, SQLModel, select

from database import get_session
from models import User


router = APIRouter()


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


def hash_password(plain_password: str) -> str:
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    if len(password_bytes) > 72:
        raise HTTPException(status_code=400, detail="Password must be at most 72 bytes.")

    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_password.decode("utf-8")


def get_user_by_email(session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def create_user(session: Session, user_data: UserRegister) -> User:
    hashed_password = hash_password(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.post("/register", response_model=UserRead)
def register(user_data: UserRegister, session: Session = Depends(get_session)):
    db_user = get_user_by_email(session, user_data.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists.")

    return create_user(session, user_data)
