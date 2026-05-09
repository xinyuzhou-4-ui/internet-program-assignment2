from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, text

from auth_user import create_activity_log, get_current_user
from database import engine, get_session
from models import Expense, ExpenseCreate, ExpenseUpdate, User


router = APIRouter()


def save_expense(session: Session, expense_data: Expense) -> Expense:
    # Save a new expense to the database.
    db_expense = Expense.model_validate(expense_data)
    session.add(db_expense)
    session.commit()
    session.refresh(db_expense)
    return db_expense


def get_user_expense(session: Session, expense_id: int, user_id: int) -> Optional[Expense]:
    # Get one expense only if it belongs to this user.
    statement = select(Expense).where(Expense.id == expense_id, Expense.user_id == user_id)
    return session.exec(statement).first()


def get_user_expenses(
    session: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[Expense]:
    # Get expense records for one user.
    statement = select(Expense).where(Expense.user_id == user_id).offset(skip).limit(limit)
    return session.exec(statement).all()


def update_user_expense(
    session: Session, expense_id: int, user_id: int, expense_data: Expense
) -> Optional[Expense]:
    # Update an expense only if it belongs to this user.
    db_expense = get_user_expense(session, expense_id, user_id)
    if not db_expense:
        return None

    update_data = expense_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_expense, key, value)

    session.add(db_expense)
    session.commit()
    session.refresh(db_expense)
    return db_expense


def delete_user_expense(session: Session, expense_id: int, user_id: int) -> bool:
    # Delete an expense only if it belongs to this user.
    db_expense = get_user_expense(session, expense_id, user_id)
    if not db_expense:
        return False

    session.delete(db_expense)
    session.commit()
    return True


@router.get("/expenses/trend")
def get_monthly_trend(current_user: User = Depends(get_current_user)):
    # Return monthly totals for the current user's expenses.
    with Session(engine) as session:
        query = text(
            """
            SELECT DATE_FORMAT(date, '%Y-%m') AS month, SUM(amount) AS total
            FROM expenses
            WHERE user_id = :user_id
            GROUP BY DATE_FORMAT(date, '%Y-%m')
            ORDER BY month
            """
        )
        results = session.exec(query, params={"user_id": current_user.id}).all()
        return [{"month": row[0], "total": float(row[1])} for row in results]


@router.get("/expenses", response_model=List[Expense])
async def get_expenses(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Return only the current user's expense records.
    return get_user_expenses(session, current_user.id)


@router.post("/expenses", response_model=Expense)
async def create_expense(
    expense_data: ExpenseCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Create an expense for the current user.
    expense = Expense(
        title=expense_data.title,
        category=expense_data.category,
        amount=expense_data.amount,
        date=date.fromisoformat(expense_data.expense_date),
        description=expense_data.description,
        user_id=current_user.id,
    )
    db_expense = save_expense(session, expense)
    create_activity_log(
        session,
        current_user.id,
        "create_expense",
        f"Created expense id {db_expense.id}",
    )
    session.refresh(db_expense)
    return db_expense


@router.put("/expenses/{expense_id}", response_model=Expense)
async def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Update the current user's expense record.
    existing_expense = get_user_expense(session, expense_id, current_user.id)
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
        user_id=existing_expense.user_id,
    )
    db_expense = update_user_expense(session, expense_id, current_user.id, expense_update)
    create_activity_log(
        session,
        current_user.id,
        "update_expense",
        f"Updated expense id {expense_id}",
    )
    session.refresh(db_expense)
    return db_expense


@router.delete("/expenses/{expense_id}")
async def delete_expense(
    expense_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Delete the current user's expense record.
    deleted = delete_user_expense(session, expense_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Expense with id {expense_id} not found.")

    create_activity_log(
        session,
        current_user.id,
        "delete_expense",
        f"Deleted expense id {expense_id}",
    )
    return {"message": f"Expense with id {expense_id} deleted successfully."}
