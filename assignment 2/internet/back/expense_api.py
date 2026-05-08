from datetime import date as DateType
from typing import List, Optional
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import field_validator
from sqlmodel import SQLModel, Session, text

from expense_app_crud import (
    Expense,
    db_create_expense,
    db_delete_expense,
    db_get_expense,
    db_get_expenses,
    db_update_expense,
    engine,
    get_session,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


# Test if the API is running
@app.get("/")
def home():
    return {"message": "Expense Tracker API is running."}


# Get total expense for each month
@app.get("/expenses/trend")
def get_monthly_trend():
    with Session(engine) as session:
        # Group data by month and add the amounts
        query = text(
            """
            SELECT DATE_FORMAT(date, '%Y-%m') AS month, SUM(amount) AS total
            FROM expenses
            GROUP BY DATE_FORMAT(date, '%Y-%m')
            ORDER BY month
            """
        )

        # Get all query results
        results = session.exec(query).all()
        return [{"month": row[0], "total": float(row[1])} for row in results]


# Get all expense records
@app.get("/expenses", response_model=List[Expense])
async def get_expenses(session: Session = Depends(get_session)):
    return await db_get_expenses(session)


# Change input data into an Expense object and save it
@app.post("/expenses", response_model=Expense)
async def create_expense(
    expense_data: ExpenseCreate, session: Session = Depends(get_session)
):
    expense = Expense(
        title=expense_data.title,
        category=expense_data.category,
        amount=expense_data.amount,
        date=DateType.fromisoformat(expense_data.expense_date),
        description=expense_data.description,
    )
    return await db_create_expense(session, expense)


# Update one expense by id
@app.put("/expenses/{expense_id}", response_model=Expense)
async def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    session: Session = Depends(get_session),
):
    existing_expense = await db_get_expense(session, expense_id)
    if not existing_expense:
        raise HTTPException(status_code=404, detail=f"Expense with id {expense_id} not found.")

    # Build a full record for update
    # If one field is missing, keep the old value
    expense_update = Expense(
        id=expense_id,
        title=expense_data.title if expense_data.title is not None else existing_expense.title,
        category=expense_data.category if expense_data.category is not None else existing_expense.category,
        # Use is not None so 0 is still allowed
        amount=expense_data.amount if expense_data.amount is not None else existing_expense.amount,
        date=DateType.fromisoformat(expense_data.expense_date)
        if expense_data.expense_date is not None
        else existing_expense.date,
        description=expense_data.description
        if expense_data.description is not None
        else existing_expense.description,
        created_at=existing_expense.created_at,
    )
    return await db_update_expense(session, expense_id, expense_update)


# Delete one expense by id
@app.delete("/expenses/{expense_id}")
async def delete_expense(expense_id: int, session: Session = Depends(get_session)):
    deleted = await db_delete_expense(session, expense_id)

    if not deleted:
        raise HTTPException(status_code=404, detail=f"Expense with id {expense_id} not found.")
    return {"message": f"Expense with id {expense_id} deleted successfully."}