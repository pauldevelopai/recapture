import sqlite3
import os

DB_NAME = "recapture.db"

def clear_listening_results():
    if not os.path.exists(DB_NAME):
        print(f"Database {DB_NAME} not found.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM listening_results")
        conn.commit()
        print("Successfully cleared listening_results table.")
    except Exception as e:
        print(f"Error clearing table: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    clear_listening_results()
