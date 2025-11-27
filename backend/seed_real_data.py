import uuid
import json
import sqlite3
from datetime import datetime, timedelta
from database import get_db_connection, init_db
from vector_store import add_documents, clear_collection

def seed_data():
    print("🌱 Starting realistic data seeding...")
    
    # Initialize DB to ensure tables exist
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- 1. Clear existing data (Optional, but good for clean state) ---
    # cursor.execute("DELETE FROM subjects")
    # cursor.execute("DELETE FROM social_media_feeds")
    # cursor.execute("DELETE FROM subject_social_posts")
    # conn.commit()
    # print("🧹 Cleared existing SQL data.")
    
    # Clear Vector Store
    clear_collection()
    print("🧹 Cleared Vector Store.")

    # --- 2. Create Realistic Subjects ---
    subjects = [
        {
            "id": str(uuid.uuid4()),
            "name": "Alex Mercer",
            "age": 19,
            "risk_level": "High",
            "notes": "Displaying signs of isolation and resentment. Frequent engagement with 'blackpill' communities."
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Jordan Lee",
            "age": 22,
            "risk_level": "Medium",
            "notes": "Politically active, but recently drifting towards extremist accelerationist rhetoric."
        }
    ]

    for sub in subjects:
        cursor.execute(
            "INSERT INTO subjects (id, name, age, risk_level, notes) VALUES (?, ?, ?, ?, ?)",
            (sub['id'], sub['name'], sub['age'], sub['risk_level'], sub['notes'])
        )
    print(f"✅ Created {len(subjects)} subjects.")

    # --- 3. Create Social Feeds & Posts ---
    
    # Alex's Feed (Incel/Blackpill)
    alex_id = subjects[0]['id']
    alex_feed_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO social_media_feeds (id, subject_id, platform, username, profile_url, status) VALUES (?, ?, ?, ?, ?, ?)",
        (alex_feed_id, alex_id, "Twitter", "alx_lonely", "https://twitter.com/alx_lonely", "active")
    )

    alex_posts = [
        "It's over for me. I'll never be enough.",
        "Just saw another happy couple. Makes me sick. They don't know how easy they have it.",
        "Women only care about looks. If you're not a Chad, you're invisible.",
        "The blackpill is the only truth. Acceptance is the first step to freedom from hope.",
        "Why even try? The game is rigged from birth.",
        "Society ignores men like us. We are the forgotten ones.",
        "Another Friday night alone. Rotting in my room while they party.",
        "I hate them. I hate them all.",
        "Normies will never understand the pain of true loneliness.",
        "Stacy wouldn't look at me if I was the last man on earth."
    ]

    for i, content in enumerate(alex_posts):
        post_id = str(uuid.uuid4())
        posted_at = (datetime.now() - timedelta(days=i)).isoformat()
        cursor.execute(
            """INSERT INTO subject_social_posts 
            (id, subject_id, feed_id, content, posted_at, platform, url, engagement_metrics, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (post_id, alex_id, alex_feed_id, content, posted_at, "Twitter", f"https://twitter.com/alx_lonely/status/{i}", json.dumps({"likes": i*2, "retweets": i}), datetime.now().isoformat())
        )

    # Jordan's Feed (Radicalization/Accelerationism)
    jordan_id = subjects[1]['id']
    jordan_feed_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO social_media_feeds (id, subject_id, platform, username, profile_url, status) VALUES (?, ?, ?, ?, ?, ?)",
        (jordan_feed_id, jordan_id, "TikTok", "jordan_awakened", "https://tiktok.com/@jordan_awakened", "active")
    )

    jordan_posts = [
        "The system isn't broken, it's working exactly as intended. To crush us.",
        "Voting changes nothing. Only direct action matters now.",
        "They want you asleep. Wake up.",
        "Burn it all down and start over. It's the only way.",
        "Peaceful protest is a joke. They laugh at us.",
        "Read Kaczynski. He predicted all of this.",
        "Industrial society and its consequences...",
        "We need to accelerate the collapse. It's inevitable anyway.",
        "Don't trust the media. They are the enemy of the people.",
        "Resistance is not futile. It's mandatory."
    ]

    for i, content in enumerate(jordan_posts):
        post_id = str(uuid.uuid4())
        posted_at = (datetime.now() - timedelta(days=i)).isoformat()
        cursor.execute(
            """INSERT INTO subject_social_posts 
            (id, subject_id, feed_id, content, posted_at, platform, url, engagement_metrics, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (post_id, jordan_id, jordan_feed_id, content, posted_at, "TikTok", f"https://tiktok.com/@jordan_awakened/video/{i}", json.dumps({"likes": i*50, "comments": i*5}), datetime.now().isoformat())
        )

    conn.commit()
    conn.close()
    print(f"✅ Created social feeds and {len(alex_posts) + len(jordan_posts)} posts.")

    # --- 4. Seed RAG Knowledge Base ---
    print("📚 Seeding RAG Knowledge Base...")
    
    rag_docs = [
        {
            "content": """
            The 'Blackpill' is a fatalistic worldview shared by some involuntary celibates (incels). 
            It posits that physical attractiveness is the primary determinant of social and romantic success, 
            and that those who lack it are doomed to misery. Key terms include 'Chad' (attractive men), 
            'Stacy' (attractive women), and 'looksmaxxing' (attempting to improve appearance, though often viewed as futile by blackpillers).
            This ideology often leads to depression, hopelessness, and in extreme cases, hatred or violence towards women and society.
            """,
            "metadata": {"source": "Incel Ideology Overview", "type": "article", "category": "Incel"}
        },
        {
            "content": """
            Accelerationism is a range of ideas in critical and social theory that proposes that social processes, 
            such as capitalist growth and technological change, should be drastically intensified to create radical social change. 
            In the context of extremism, 'accelerationism' often refers to the belief that modern society is irredeemable 
            and should be pushed towards collapse to establish a new order. This can manifest as support for acts of chaos, 
            violence, or destabilization.
            """,
            "metadata": {"source": "Understanding Accelerationism", "type": "report", "category": "Extremism"}
        },
        {
            "content": """
            Radicalization is the process by which an individual or group comes to adopt increasingly extreme political, 
            social, or religious ideals and aspirations that reject or undermine the status quo or contemporary ideas and expressions of the nation. 
            Pathways to radicalization often involve a sense of grievance, alienation, and the search for identity and belonging. 
            Online communities can act as echo chambers that reinforce these extreme views.
            """,
            "metadata": {"source": "Radicalization Pathways", "type": "academic", "category": "Psychology"}
        }
    ]

    add_documents(
        documents=[d['content'] for d in rag_docs],
        metadatas=[d['metadata'] for d in rag_docs],
        ids=[str(uuid.uuid4()) for _ in rag_docs]
    )
    print(f"✅ Added {len(rag_docs)} documents to Knowledge Base.")
    
    print("🎉 Seeding Complete! The app is now ready for verification.")

if __name__ == "__main__":
    seed_data()
