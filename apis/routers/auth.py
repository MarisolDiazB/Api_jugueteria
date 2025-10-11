"""
Módulo de autenticación para la API de Juguetería.
--------------------------------------------------

Este módulo gestiona el registro, inicio de sesión y validación de usuarios mediante
JWT (JSON Web Tokens). Implementa autenticación con formulario y con JSON, usando
OAuth2 y contraseñas encriptadas con `passlib`.

Incluye:
    - Creación de tokens JWT.
    - Registro de nuevos usuarios.
    - Verificación de contraseñas.
    - Obtención de usuario autenticado.
"""
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
    """Datos de inicio de sesión por JSON.
    
    Atributos:
        username (EmailStr): Correo electrónico del usuario.
        password (str): Contraseña en texto plano.
    """
    username: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Respuesta al iniciar sesión.

    Atributos:
        access_token (str): Token JWT generado tras la autenticación.
        token_type (str): Tipo de token, por defecto "bearer".
        user (UserOut): Información pública del usuario autenticado.
    """
    access_token: str
    token_type: str = "bearer"
    user: UserOut


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verifica si la contraseña ingresada coincide con su hash almacenado.

    Args:
        plain_password (str): Contraseña en texto plano.
        password_hash (str): Contraseña encriptada almacenada.

    Returns:
        bool: `True` si coinciden, `False` en caso contrario.
    """

    return pwd_context.verify(plain_password, password_hash)


def get_password_hash(password: str) -> str:
    """Genera el hash seguro de una contraseña usando PBKDF2-SHA256.

    Args:
        password (str): Contraseña en texto plano.

    Raises:
        HTTPException: Si la contraseña supera los 256 caracteres.

    Returns:
        str: Hash encriptado de la contraseña.
    """
    if len(password) > 256:
        raise HTTPException(status_code=400, detail="La contraseña es demasiado larga")
    return pwd_context.hash(password)


def create_access_token(*, data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT firmado con una fecha de expiración.

    Args:
        data (dict): Datos a codificar dentro del token (claims).
        expires_delta (Optional[timedelta]): Tiempo de expiración. Si no se
            especifica, usa el valor por defecto de `ACCESS_TOKEN_EXPIRE_MINUTES`.

    Returns:
        str: Token JWT firmado.
    """
    to_encode = data.copy()
    now = datetime.now(tz=timezone.utc)
    expires = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"iat": int(now.timestamp()), "exp": int(expires.timestamp())})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    """Autentica un usuario verificando su correo y contraseña.

    Args:
        db (Session): Sesión activa de SQLAlchemy.
        username (str): Correo electrónico del usuario.
        password (str): Contraseña en texto plano.

    Returns:
        Optional[models.User]: Instancia del usuario autenticado o `None` si falla.
    """
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
    """Crea un nuevo usuario y valida duplicados o contraseñas débiles.

    Args:
        db (Session): Sesión activa de SQLAlchemy.
        payload (UserCreate): Datos del usuario a registrar.

    Raises:
        HTTPException: Si el correo ya está registrado o la contraseña es débil.

    Returns:
        models.User: Instancia del nuevo usuario creado.
    """
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
    """Obtiene el usuario autenticado a partir de un token JWT Bearer.

    Args:
        token (str): Token JWT del encabezado `Authorization`.
        db (Session): Sesión de base de datos.

    Raises:
        HTTPException: Si el token es inválido, ha expirado o el usuario está desactivado.

    Returns:
        models.User: Instancia del usuario autenticado.
    """
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
    """Endpoint para registrar un nuevo usuario en la base de datos.

    Args:
        user (UserCreate): Datos del usuario a registrar.
        db (Session): Sesión activa de la base de datos.

    Returns:
        UserOut: Representación pública del usuario creado.
    """
    db_user = create_user(db, user)
    return db_user


@router.post("/login", response_model=LoginResponse)
def login_user_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Autentica a un usuario mediante formulario OAuth2 (para Swagger o Postman).

    Args:
        form_data (OAuth2PasswordRequestForm): Datos de inicio de sesión enviados desde el formulario.
        db (Session): Sesión activa de base de datos.

    Raises:
        HTTPException: Si las credenciales son incorrectas.

    Returns:
        LoginResponse: Token JWT y datos del usuario autenticado.
    """
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
    """Autentica a un usuario mediante JSON (ideal para clientes externos).

    Args:
        payload (LoginRequest): Datos del usuario (correo y contraseña).
        db (Session): Sesión activa de base de datos.

    Raises:
        HTTPException: Si las credenciales son incorrectas.

    Returns:
        LoginResponse: Token JWT y datos del usuario autenticado.
    """
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
    """Obtiene la información del usuario autenticado actual.

    Args:
        current_user (models.User): Usuario autenticado obtenido del token.

    Returns:
        UserOut: Datos públicos del usuario autenticado.
    """
    return current_user
