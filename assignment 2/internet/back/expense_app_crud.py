from typing import List, Optional

from sqlmodel import Session, select

from models import Expense

# CRUD functions for expenses


# Add one new expense record
async def db_create_expense(session: Session, expense_create: Expense) -> Expense:
    # Check and build the expense object
    new_expense = Expense.model_validate(expense_create)
    # Add it to the session
    session.add(new_expense)
    # Save it to the database
    session.commit()
    # Get the newest data back
    session.refresh(new_expense)
    return new_expense


# Get one expense by id
async def db_get_expense(
    session: Session, expense_id: int, user_id: Optional[int] = None
) -> Optional[Expense]:
    if user_id is None:
        return session.get(Expense, expense_id)

    statement = select(Expense).where(
        Expense.id == expense_id, Expense.user_id == user_id
    )
    return session.exec(statement).first()


# Get many expense records
# skip is how many rows to skip, and limit is the max number to return
async def db_get_expenses(
    session: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[Expense]:
    # Build the query
    statement = (
        select(Expense).where(Expense.user_id == user_id).offset(skip).limit(limit)
    )
    return session.exec(statement).all()


# Update one expense record
async def db_update_expense(
    session: Session, expense_id: int, user_id: int, expense_update: Expense
) -> Optional[Expense]:
    # Find the old record first
    expense = await db_get_expense(session, expense_id, user_id)
    if not expense:
        return None

    # Change the model into a dictionary
    update_data = expense_update.model_dump(exclude_unset=True)

    # Update each field one by one
    for key, value in update_data.items():
        setattr(expense, key, value)

    # Save the updated record
    session.add(expense)
    session.commit()
    session.refresh(expense)
    return expense


# Delete one expense by id
async def db_delete_expense(session: Session, expense_id: int, user_id: int) -> bool:
    # Find the record first
    expense = await db_get_expense(session, expense_id, user_id)
    if not expense:
        return False

    # Delete the record
    session.delete(expense)
    session.commit()
    return True
