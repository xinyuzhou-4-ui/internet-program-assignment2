from datetime import date, datetime
from typing import Optional

from pydantic import field_validator
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50)
    email: str = Field(max_length=100)
    hashed_password: str = Field(max_length=255)
    role: str = Field(default="user", max_length=20)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)


class Expense(SQLModel, table=True):
    __tablename__ = "expenses"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=100)
    category: str = Field(max_length=50)
    amount: float
    date: date
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")


class UserActivity(SQLModel, table=True):
    __tablename__ = "user_activities"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    activity_type: str = Field(max_length=50)
    detail: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class ExpenseCreate(SQLModel):
    title: str
    category: str
    amount: float
    expense_date: str
    description: Optional[str] = None

    @field_validator("expense_date")
    @classmethod
    def validate_expense_date(cls, value: str) -> str:
        date.fromisoformat(value)
        return value


class ExpenseUpdate(SQLModel):
    title: Optional[str] = None
    category: Optional[str] = None
    amount: Optional[float] = None
    expense_date: Optional[str] = None
    description: Optional[str] = None
