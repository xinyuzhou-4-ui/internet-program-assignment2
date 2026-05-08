from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from admin_routes import router as admin_router
from auth_user import router as auth_router
from database import create_db_and_tables
from expense_routes import router as expense_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(expense_router)
app.include_router(auth_router)
app.include_router(admin_router)


@app.on_event("startup")
def start_app():
    create_db_and_tables()


# Test if the API is running
@app.get("/")
def home():
    return {"message": "Expense Tracker API is running."}
