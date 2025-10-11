"""
Módulo de conexión a la base de datos para la API de Juguetería.
================================================================

Configura la conexión con SQL Server (u otro motor compatible),
utilizando SQLAlchemy ORM y variables de entorno definidas en `.env`.

Incluye:
    - Creación del motor de base de datos (`engine`)
    - Configuración de sesión (`SessionLocal`)
    - Clase base declarativa (`Base`)
    - Dependencia `get_db()` para inyección en rutas FastAPI
    - Funciones auxiliares `create_tables()` y `drop_tables()`
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=True  
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)

def drop_tables():
    Base.metadata.drop_all(bind=engine)


if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            print("✅ Conexión exitosa a SQL Server")
    except Exception as e:
        print("❌ Error al conectar:", e)
