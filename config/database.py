from typing import Generator

from sqlmodel import SQLModel, create_engine, Session
from .settings import settings

SQLAlchemy_DATABASE_URL = settings.DATABASE_URL

# Create engine with SQL statement logging enabled
engine = create_engine(SQLAlchemy_DATABASE_URL, echo=settings.ECHO_SQL)


# Function to create database tables from SQLModel classes
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
