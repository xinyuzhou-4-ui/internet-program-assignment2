from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

import models  # Register SQLModel tables before create_all.
from auth_user import router as auth_router
from database import engine
from expense_routes import router as expense_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SQLModel.metadata.create_all(engine)

app.include_router(auth_router)
app.include_router(expense_router)


# Test if the API is running
@app.get("/")
def home():
    return {"message": "Expense Tracker API is running."}
