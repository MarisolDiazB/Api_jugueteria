import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.connection import get_db
from apis import models
from apis.schemas import UserCreate, UserOut


load_dotenv()


SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-me")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth", tags=["Autenticación"])


class LoginRequest(BaseModel):
    """Datos de inicio de sesión por JSON."""
    username: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Respuesta de autenticación con token y datos del usuario."""
    access_token: str
    token_type: str = "bearer"
    user: UserOut


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Valida una contraseña en texto plano contra su hash."""
    return pwd_context.verify(plain_password, password_hash)


def get_password_hash(password: str) -> str:
    """Genera el hash seguro de una contraseña con un límite de longitud."""
    if len(password) > 256:
        raise HTTPException(status_code=400, detail="La contraseña es demasiado larga")
    return pwd_context.hash(password)


def create_access_token(*, data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT con reclamaciones estándar y expiración."""
    to_encode = data.copy()
    now = datetime.now(tz=timezone.utc)
    expires = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"iat": int(now.timestamp()), "exp": int(expires.timestamp())})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    """Autentica al usuario por correo y contraseña."""
    user = (
        db.query(models.User)
        .filter(func.lower(models.User.email) == username.strip().lower())
        .first()
    )
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(db: Session, payload: UserCreate) -> models.User:
    """Crea un nuevo usuario aplicando validaciones básicas."""
    email = payload.email.strip().lower()
    exists = db.query(models.User).filter(func.lower(models.User.email) == email).first()
    if exists:
        raise HTTPException(status_code=409, detail="Email ya registrado")
    if len(payload.password) < 8:
        raise HTTPException(status_code=422, detail="La contraseña debe tener al menos 8 caracteres")

    user = models.User(
        email=email,
        hashed_password=get_password_hash(payload.password),
        is_active=True,
        creado_por=payload.creado_por,
        actualizado_por=payload.actualizado_por,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    """Obtiene el usuario autenticado a partir del token Bearer."""
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exc
        user_id = UUID(sub)
    except JWTError:
        raise credentials_exc
    except Exception:
        raise credentials_exc

    user = db.get(models.User, user_id)
    if user is None:
        raise credentials_exc
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Cuenta desactivada")
    return user


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Registra un nuevo usuario y devuelve su representación pública."""
    db_user = create_user(db, user)
    return db_user


@router.post("/login", response_model=LoginResponse)
def login_user_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Autentica mediante formulario OAuth2 compatible con Swagger."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return LoginResponse(access_token=token, user=user)


@router.post("/login_json", response_model=LoginResponse)
def login_user_json(payload: LoginRequest, db: Session = Depends(get_db)):
    """Autentica mediante JSON con usuario y contraseña."""
    user = authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return LoginResponse(access_token=token, user=user)


@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """Devuelve los datos del usuario autenticado."""
    return current_user
