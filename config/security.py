from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from config.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

def create_token(token_type: str, data: dict):
    to_encode = data.copy()
    expire: datetime = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    match token_type:
        case 'access':
            expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        case 'refresh':
            expire = datetime.now() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

