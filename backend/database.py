import sqlite3
from typing import List, Optional
from .models import DisinformationTrend

import os
DB_NAME = os.getenv("DB_NAME", "recapture.db")

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

    # Subjects Table (formerly Profiles)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subjects (
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
        subject_id TEXT,
        content TEXT,
        source_url TEXT,
        timestamp TEXT,
        analysis_id TEXT,
        detected_trends TEXT, -- Stored as JSON
        FOREIGN KEY(subject_id) REFERENCES subjects(id)
    )
    ''')
    
    # Authorities Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS authorities (
        id TEXT PRIMARY KEY,
        subject_id TEXT,
        name TEXT,
        role TEXT,
        relation TEXT,
        FOREIGN KEY(subject_id) REFERENCES subjects(id)
    )
    ''')

    # Sources Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sources (
        id TEXT PRIMARY KEY,
        name TEXT,
        url TEXT,
        type TEXT,
        status TEXT,
        last_scraped TEXT
    )
    ''')

    # Raw Content Table (Pipeline)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS raw_content (
        id TEXT PRIMARY KEY,
        source_id TEXT,
        content TEXT,
        url TEXT,
        timestamp TEXT,
        status TEXT, -- pending, approved, discarded, trained
        analysis_summary TEXT,
        risk_score REAL
    )
    ''')

    # Listening Results Table (Live Feed)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS listening_results (
        id TEXT PRIMARY KEY,
        source_platform TEXT,
        author TEXT,
        content TEXT,
        timestamp TEXT,
        matched_trend_id TEXT,
        matched_trend_topic TEXT,
        severity TEXT,
        url TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
