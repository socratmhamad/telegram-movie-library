from database.models import get_db_url, init_db
from sqlalchemy import text
from backend.config import get_database_url, get_database_path
import traceback

def run_migration():
    db_url = get_db_url(get_database_url(), get_database_path())
    Session = init_db(db_url)
    print(f"Migrating database: {db_url}")
    
    with Session() as db:
        try:
            db.execute(text("ALTER TABLE libraries ADD COLUMN display_order INTEGER DEFAULT 0"))
            print("Successfully added display_order to libraries.")
        except Exception as e:
            print(f"Skipping libraries column creation (might already exist): {e}")
            db.rollback()

        try:
            db.execute(text("ALTER TABLE tv_libraries ADD COLUMN display_order INTEGER DEFAULT 0"))
            print("Successfully added display_order to tv_libraries.")
        except Exception as e:
            print(f"Skipping tv_libraries column creation (might already exist): {e}")
            db.rollback()

        try:
            # Set default display_order to id if null or 0 so initial order matches ID sequence
            db.execute(text("UPDATE libraries SET display_order = id WHERE display_order IS NULL OR display_order = 0"))
            db.execute(text("UPDATE tv_libraries SET display_order = id WHERE display_order IS NULL OR display_order = 0"))
            print("Initialized display_order values from library ids.")
        except Exception as e:
            print(f"Skipping display_order initialization: {e}")
            db.rollback()

        db.commit()
    print("Migration complete.")

if __name__ == "__main__":
    run_migration()
