"""
Script de migración de la base de datos de la API Juguetería 🧩
===============================================================

Este módulo elimina y recrea todas las tablas ORM definidas en `apis.models`,
utilizando las funciones `create_tables()` y `drop_tables()` del módulo `database.connection`.

Uso:
    python migrate_database.py

Advertencia:
    Este proceso elimina TODAS las tablas y sus datos.
    Úsalo únicamente en entornos de desarrollo o pruebas.
"""
from database.connection import create_tables, drop_tables
import apis.models

def migrate_database():
    print("🔄 Iniciando migración...")
    try:
        drop_tables()
        print("🗑️  Tablas eliminadas")
        create_tables()
        print("✅ Tablas creadas correctamente")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    migrate_database()


