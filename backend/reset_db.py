import os
import sqlite3
from .database import init_db, DB_NAME

def reset_database():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Deleted existing database: {DB_NAME}")
    else:
        print(f"No existing database found at {DB_NAME}")
    
    init_db()
    print("Initialized new database with updated schema.")

if __name__ == "__main__":
    reset_database()
