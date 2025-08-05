from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from starlette.responses import JSONResponse

from config.settings import settings
from routes.task_routes import router as task_router
from routes.user_routes import router as user_router
from routes.auth_routes import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ya no es necesaria gracias a alembic
    # create_db_and_tables()
    yield
    print("Apagando la app...")


app = FastAPI(
    lifespan=lifespan,
    debug=settings.DEBUG,
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
)


@app.get('/')
async def root():
    return JSONResponse({'message': 'Welcome to the todo app API :)', 'status': status.HTTP_200_OK})


app.include_router(user_router)
app.include_router(task_router)
app.include_router(auth_router)
