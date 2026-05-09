from typing import List, Optional
from sqlmodel import Session, select
from models import Expense


async def create_expense(session: Session, expense_data: Expense) -> Expense:
    new_expense = Expense.model_validate(expense_data)
    session.add(new_expense)
    session.commit()
    session.refresh(new_expense)
    return new_expense


async def get_user_expense(
    session: Session, expense_id: int, user_id: int
) -> Optional[Expense]:
    statement = select(Expense).where(Expense.id == expense_id, Expense.user_id == user_id)
    return session.exec(statement).first()


async def get_user_expenses(
    session: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[Expense]:
    statement = select(Expense).where(Expense.user_id == user_id).offset(skip).limit(limit)
    return session.exec(statement).all()


async def update_expense(
    session: Session, expense_id: int, user_id: int, expense_data: Expense
) -> Optional[Expense]:
    expense = await get_user_expense(session, expense_id, user_id)
    if not expense:
        return None

    update_data = expense_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(expense, key, value)

    session.add(expense)
    session.commit()
    session.refresh(expense)
    return expense


async def delete_expense(session: Session, expense_id: int, user_id: int) -> bool:
    expense = await get_user_expense(session, expense_id, user_id)
    if not expense:
        return False

    session.delete(expense)
    session.commit()
    return True
