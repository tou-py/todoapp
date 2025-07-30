from contextlib import asynccontextmanager
from fastapi import FastAPI

from config.database import create_db_and_tables
from routes.user_routes import router as user_router
from routes.task_routes import router as task_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    print("Apagando la app...")


app = FastAPI(
    lifespan=lifespan,
)

app.include_router(user_router)
app.include_router(task_router)