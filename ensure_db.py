"""
Script de inicialización de base de datos Juguetería 🧸
========================================================

Este script se conecta al servidor SQL Server (o cualquier motor compatible con SQLAlchemy)
y crea la base de datos `jugueteria` si aún no existe.

Uso:
    python create_database.py

Requisitos:
    - Archivo `.env` con la variable DATABASE_URL (cadena de conexión válida)
    - Motor SQL Server accesible (por ejemplo: localhost o remoto)
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
url_master = os.getenv("DATABASE_URL")
engine = create_engine(url_master, pool_pre_ping=True)

with engine.connect() as conn:
    conn.execute(text("IF DB_ID('jugueteria') IS NULL CREATE DATABASE jugueteria;"))
    print("✅ BD 'jugueteria' lista")
