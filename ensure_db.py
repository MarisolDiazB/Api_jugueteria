from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
url_master = os.getenv("DATABASE_URL")
engine = create_engine(url_master, pool_pre_ping=True)

with engine.connect() as conn:
    conn.execute(text("IF DB_ID('jugueteria') IS NULL CREATE DATABASE jugueteria;"))
    print("✅ BD 'jugueteria' lista")
