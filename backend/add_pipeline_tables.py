from .database import init_db

if __name__ == "__main__":
    print("Applying database migration (adding pipeline tables)...")
    init_db()
    print("Migration complete.")
