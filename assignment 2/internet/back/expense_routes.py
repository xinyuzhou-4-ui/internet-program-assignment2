from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, text

from auth_user import get_current_user
from database import engine, get_session
from expense_crud import (
    create_expense as db_create_expense,
    delete_expense as db_delete_expense,
    get_expense as db_get_expense,
    get_expenses as db_get_expenses,
    update_expense as db_update_expense,
)
from models import Expense, ExpenseCreate, ExpenseUpdate, User


router = APIRouter()


@router.get("/expenses/trend")
def get_monthly_trend(current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        query = text(
            """
            SELECT DATE_FORMAT(date, '%Y-%m') AS month, SUM(amount) AS total
            FROM expenses
            GROUP BY DATE_FORMAT(date, '%Y-%m')
            ORDER BY month
            """
        )
        results = session.exec(query).all()
        return [{"month": row[0], "total": float(row[1])} for row in results]


@router.get("/expenses", response_model=List[Expense])
async def get_expenses(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await db_get_expenses(session)


@router.post("/expenses", response_model=Expense)
async def create_expense(
    expense_data: ExpenseCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    expense = Expense(
        title=expense_data.title,
        category=expense_data.category,
        amount=expense_data.amount,
        date=date.fromisoformat(expense_data.expense_date),
        description=expense_data.description,
    )
    return await db_create_expense(session, expense)


@router.put("/expenses/{expense_id}", response_model=Expense)
async def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    existing_expense = await db_get_expense(session, expense_id)
    if not existing_expense:
        raise HTTPException(status_code=404, detail=f"Expense with id {expense_id} not found.")

    expense_update = Expense(
        id=expense_id,
        title=expense_data.title if expense_data.title is not None else existing_expense.title,
        category=expense_data.category if expense_data.category is not None else existing_expense.category,
        amount=expense_data.amount if expense_data.amount is not None else existing_expense.amount,
        date=date.fromisoformat(expense_data.expense_date)
        if expense_data.expense_date is not None
        else existing_expense.date,
        description=expense_data.description
        if expense_data.description is not None
        else existing_expense.description,
        created_at=existing_expense.created_at,
    )
    return await db_update_expense(session, expense_id, expense_update)


@router.delete("/expenses/{expense_id}")
async def delete_expense(
    expense_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    deleted = await db_delete_expense(session, expense_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Expense with id {expense_id} not found.")

    return {"message": f"Expense with id {expense_id} deleted successfully."}
