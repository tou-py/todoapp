from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette import status
from starlette.responses import JSONResponse

from config.database import create_db_and_tables
from routes.task_routes import router as task_router
from routes.user_routes import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    print("Apagando la app...")


app = FastAPI(
    lifespan=lifespan,
)

@app.get('/')
async def root():
    return JSONResponse({'message': 'Welcome to the todo app API :)', 'status': status.HTTP_200_OK})

app.include_router(user_router)
app.include_router(task_router)
