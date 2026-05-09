import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, SQLModel, select

from database import get_session
from models import User, UserActivity


router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)
SECRET_KEY = os.getenv("SECRET_KEY", "expense-tracker-secret-key-for-jwt-2026")
ALGORITHM = "HS256"


class UserRegister(SQLModel):
    # Request body for user registration.
    username: str
    email: str
    password: str


class UserRead(SQLModel):
    # User response model. It does not include hashed_password.
    id: int
    username: str
    email: str
    role: str
    is_active: bool


class UserLogin(SQLModel):
    # Request body for user login.
    email: str
    password: str


class TokenRead(SQLModel):
    # Response model returned after successful login.
    access_token: str
    token_type: str = "bearer"


def hash_password(plain_password: str) -> str:
    # Hash password before saving it to the database.
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    if len(password_bytes) > 72:
        raise HTTPException(status_code=400, detail="Password must be at most 72 bytes.")

    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Compare a login password with the saved password hash.
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > 72:
        return False
    return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))


def create_access_token(db_user: User) -> str:
    # Create a JWT token for the logged in user.
    payload = {
        "user_id": db_user.id,
        "email": db_user.email,
        "role": db_user.role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=2),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_user_by_email(session: Session, email: str) -> User | None:
    # Find one user by email.
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_user_by_id(session: Session, user_id: int) -> User | None:
    # Find one user by id.
    return session.get(User, user_id)


def create_user(session: Session, user_data: UserRegister) -> User:
    # Create a new user with a hashed password.
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


def create_activity_log(
    session: Session, user_id: int, action: str, detail: str | None = None
) -> UserActivity:
    # Save one activity record for a user action.
    activity = UserActivity(user_id=user_id, action=action, detail=detail)
    session.add(activity)
    session.commit()
    session.refresh(activity)
    return activity


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    # Read and verify the Bearer token, then return the current user.
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Not authenticated.")

    token = credentials.credentials
    error = HTTPException(status_code=401, detail="Invalid or expired token.")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except jwt.InvalidTokenError:
        raise error

    # The token should identify the logged in user.
    user_id = payload.get("user_id") or payload.get("sub")
    email = payload.get("email")
    role = payload.get("role")

    db_user = None
    if user_id is not None:
        try:
            db_user = get_user_by_id(session, int(user_id))
        except ValueError:
            raise error
    if db_user is None and email:
        db_user = get_user_by_email(session, email)

    if db_user is None:
        raise error
    if not db_user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive.")
    if email and db_user.email != email:
        raise error
    if role and db_user.role != role:
        raise error

    return db_user


@router.post("/register", response_model=UserRead)
def register(user_data: UserRegister, session: Session = Depends(get_session)):
    # Register a new user if the email is not already used.
    db_user = get_user_by_email(session, user_data.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists.")

    return create_user(session, user_data)


@router.post("/login", response_model=TokenRead)
def login(user_data: UserLogin, session: Session = Depends(get_session)):
    # Check email and password, then return an access token.
    db_user = get_user_by_email(session, user_data.email)
    if db_user is None or not verify_password(user_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not db_user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive.")

    create_activity_log(session, db_user.id, "login", "User logged in")
    access_token = create_access_token(db_user)
    return TokenRead(access_token=access_token)
