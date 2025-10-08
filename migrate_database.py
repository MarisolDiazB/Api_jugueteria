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
