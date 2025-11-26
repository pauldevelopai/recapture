#!/usr/bin/env python
"""Initialize database with all tables including new social media and clone tables"""
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db

if __name__ == "__main__":
    print("Initializing database with all tables...")
    init_db()
    print("✅ Database initialized successfully!")
    print("Tables created:")
    print("  - subjects")
    print("  - content_logs")
    print("  - authorities")
    print("  - trends")
    print("  - sources")
    print("  - raw_content")
    print("  - listening_results")
    print("  - social_media_feeds (NEW)")
    print("  - subject_social_posts (NEW)")
    print("  - risk_profile_analyses (NEW)")
    print("  - digital_clones (NEW)")
    print("  - clone_conversations (NEW)")
