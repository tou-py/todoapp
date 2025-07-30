from sqlmodel import SQLModel, create_engine

# SQLite connection string
sqlite_file_name = "tasks.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Create engine with SQL statement logging enabled
engine = create_engine(sqlite_url, echo=True)


# Function to create database tables from SQLModel classes
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
