import sqlite3
from typing import List, Optional
from .models import DisinformationTrend

DB_NAME = "recapture.db"

def init_db():
    """Initialize the SQLite database with required tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Trends Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trends (
        id TEXT PRIMARY KEY,
        topic TEXT NOT NULL,
        description TEXT,
        severity TEXT,
        common_phrases TEXT, -- Stored as JSON
        counter_arguments TEXT, -- Stored as JSON
        sources TEXT -- Stored as JSON
    )
    ''')

    # Kid Profiles Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS profiles (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER,
        risk_level TEXT,
        notes TEXT
    )
    ''')

    # Content Logs Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS content_logs (
        id TEXT PRIMARY KEY,
        profile_id TEXT,
        content TEXT,
        source_url TEXT,
        timestamp TEXT,
        analysis_id TEXT,
        detected_trends TEXT, -- Stored as JSON
        FOREIGN KEY(profile_id) REFERENCES profiles(id)
    )
    ''')
    
    # Authorities Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS authorities (
        id TEXT PRIMARY KEY,
        profile_id TEXT,
        name TEXT,
        role TEXT,
        relation TEXT,
        FOREIGN KEY(profile_id) REFERENCES profiles(id)
    )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
