import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlmodel import Session, create_engine


load_dotenv(Path(__file__).with_name(".env"))

db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "3306")
db_user = os.getenv("DB_USER", "root")
db_password = quote_plus(os.getenv("DB_PASSWORD", ""))
db_name = os.getenv("DB_NAME", "expense_tracker")

DATABASE_URL = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    """Return a database session."""
    with Session(engine) as session:
        yield session
