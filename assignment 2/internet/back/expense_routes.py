from datetime import date as DateType
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import field_validator
from sqlmodel import SQLModel, Session, text

from auth_user import create_activity_log, get_current_user
from database import get_session
from expense_app_crud import (
    db_create_expense,
    db_delete_expense,
    db_get_expense,
    db_get_expenses,
    db_update_expense,
)
from models import Expense, User

router = APIRouter()


# Check input data format
class ExpenseCreate(SQLModel):
    title: str
    category: str
    amount: float
    expense_date: str
    description: Optional[str] = None

    # Check the date format
    @field_validator("expense_date")
    @classmethod
    def validate_expense_date(cls, value: str) -> str:
        DateType.fromisoformat(value)
        return value


# All fields are optional for update
class ExpenseUpdate(SQLModel):
    title: Optional[str] = None
    category: Optional[str] = None
    amount: Optional[float] = None
    expense_date: Optional[str] = None
    description: Optional[str] = None


# Get total expense for each month
@router.get("/expenses/trend")
def get_monthly_trend(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Group data by month and add the amounts
    query = text("""
        SELECT DATE_FORMAT(date, '%Y-%m') AS month, SUM(amount) AS total
        FROM expenses
        WHERE user_id = :user_id
        GROUP BY DATE_FORMAT(date, '%Y-%m')
        ORDER BY month
        """).bindparams(user_id=current_user.id)

    # Get all query results
    results = session.exec(query).all()
    return [{"month": row[0], "total": float(row[1])} for row in results]


# Get all expense records
@router.get("/expenses", response_model=List[Expense])
async def get_expenses(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await db_get_expenses(session, current_user.id)


# Change input data into an Expense object and save it
@router.post("/expenses", response_model=Expense)
async def create_expense(
    expense_data: ExpenseCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    expense = Expense(
        user_id=current_user.id,
        title=expense_data.title,
        category=expense_data.category,
        amount=expense_data.amount,
        date=DateType.fromisoformat(expense_data.expense_date),
        description=expense_data.description,
    )
    new_expense = await db_create_expense(session, expense)
    await create_activity_log(
        session,
        current_user.id,
        "create_expense",
        f"Created expense {new_expense.id}: {new_expense.title}",
    )
    return new_expense


# Update one expense by id
@router.put("/expenses/{expense_id}", response_model=Expense)
async def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    existing_expense = await db_get_expense(session, expense_id, current_user.id)
    if not existing_expense:
        raise HTTPException(
            status_code=404, detail=f"Expense with id {expense_id} not found."
        )

    # Build a full record for update
    # If one field is missing, keep the old value
    expense_update = Expense(
        id=expense_id,
        user_id=existing_expense.user_id,
        title=(
            expense_data.title
            if expense_data.title is not None
            else existing_expense.title
        ),
        category=(
            expense_data.category
            if expense_data.category is not None
            else existing_expense.category
        ),
        # Use is not None so 0 is still allowed
        amount=(
            expense_data.amount
            if expense_data.amount is not None
            else existing_expense.amount
        ),
        date=(
            DateType.fromisoformat(expense_data.expense_date)
            if expense_data.expense_date is not None
            else existing_expense.date
        ),
        description=(
            expense_data.description
            if expense_data.description is not None
            else existing_expense.description
        ),
        created_at=existing_expense.created_at,
    )
    updated_expense = await db_update_expense(
        session, expense_id, current_user.id, expense_update
    )
    await create_activity_log(
        session,
        current_user.id,
        "update_expense",
        f"Updated expense {updated_expense.id}: {updated_expense.title}",
    )
    return updated_expense


# Delete one expense by id
@router.delete("/expenses/{expense_id}")
async def delete_expense(
    expense_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    existing_expense = await db_get_expense(session, expense_id, current_user.id)
    if not existing_expense:
        raise HTTPException(
            status_code=404, detail=f"Expense with id {expense_id} not found."
        )

    deleted_title = existing_expense.title
    deleted = await db_delete_expense(session, expense_id, current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=404, detail=f"Expense with id {expense_id} not found."
        )

    await create_activity_log(
        session,
        current_user.id,
        "delete_expense",
        f"Deleted expense {expense_id}: {deleted_title}",
    )
    return {"message": f"Expense with id {expense_id} deleted successfully."}
