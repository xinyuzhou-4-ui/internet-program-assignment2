from urllib.parse import quote_plus

from sqlmodel import Session, create_engine

# Set the database connection
username = "root"
raw_password = "1234"
password = quote_plus(raw_password)
database_name = "expense_tracker"
DATABASE_URL = f"mysql+pymysql://{username}:{password}@localhost:3306/{database_name}"
engine = create_engine(DATABASE_URL, echo=True)


# Get one database session
def get_session():
    """Return a database session."""
    with Session(engine) as session:
        yield session
