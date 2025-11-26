import sys
import os
import json
from datetime import datetime, timedelta

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
os.chdir(parent_dir)  # Change to project root where recapture.db is

from backend.database import get_db_connection
import uuid

def add_mock_posts():
    """Add realistic mock social media posts for testing the digital clone"""
    
    subject_id = "test-sarah-1"
    
    # Realistic posts that show personality, interests, and communication style
    mock_posts = [
        {
            "content": "Just joined another Discord server for anime fans. Finally found people who get my obsession with psychological thrillers! 🎭",
            "platform": "Twitter",
            "posted_at": (datetime.now() - timedelta(days=2)).isoformat()
        },
        {
            "content": "Why do adults always say 'you'll understand when you're older'? Like maybe if you actually explained things instead of dismissing us...",
            "platform": "Twitter",
            "posted_at": (datetime.now() - timedelta(days=3)).isoformat()
        },
        {
            "content": "My online friends are literally the only ones who understand me. School is just full of fake people pretending to care.",
            "platform": "Instagram",
            "posted_at": (datetime.now() - timedelta(days=5)).isoformat()
        },
        {
            "content": "Been researching different worldviews and philosophies. Mainstream media doesn't want you asking these questions... 🤔",
            "platform": "Twitter",
            "posted_at": (datetime.now() - timedelta(days=7)).isoformat()
        },
        {
            "content": "Parents keep saying I spend too much time online. But at least online people are honest about who they are.",
            "platform": "Twitter",
            "posted_at": (datetime.now() - timedelta(days=8)).isoformat()
        },
        {
            "content": "Finished reading another book on critical thinking. Why don't they teach this stuff in school? Oh wait, I know why... 👁️",
            "platform": "Instagram",
            "posted_at": (datetime.now() - timedelta(days=10)).isoformat()
        },
        {
            "content": "Sometimes I wonder if anyone in my real life actually gets me. Online is where I can be myself without judgment.",
            "platform": "Twitter",
            "posted_at": (datetime.now() - timedelta(days=12)).isoformat()
        },
        {
            "content": "Just realized how much the education system is designed to create compliant workers, not free thinkers. Mind = blown 🤯",
            "platform": "Twitter",
            "posted_at": (datetime.now() - timedelta(days=14)).isoformat()
        },
        {
            "content": "My Discord friends recommended some really eye-opening content. Finally understanding how the world actually works.",
            "platform": "Instagram",
            "posted_at": (datetime.now() - timedelta(days=15)).isoformat()
        },
        {
            "content": "Family dinner was awkward again. They don't even try to understand my perspective. Whatever, I've got my real community online.",
            "platform": "Twitter",
            "posted_at": (datetime.now() - timedelta(days=17)).isoformat()
        },
        {
            "content": "Love how my online friends actually engage with ideas instead of just repeating what they heard on TV. Real conversations happen online.",
            "platform": "Instagram",
            "posted_at": (datetime.now() - timedelta(days=20)).isoformat()
        },
        {
            "content": "Teacher tried to debate me today. She couldn't even defend her arguments lol. Schools don't want you to think critically.",
            "platform": "Twitter",
            "posted_at": (datetime.now() - timedelta(days=22)).isoformat()
        }
    ]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get the feed_id for this subject
    cursor.execute("SELECT id FROM social_media_feeds WHERE subject_id = ? LIMIT 1", (subject_id,))
    feed_row = cursor.fetchone()
    if not feed_row:
        print("❌ No social media feed found for this subject. Add a feed first!")
        conn.close()
        return
    
    feed_id = feed_row['id']
    
    # Delete existing posts for this subject
    cursor.execute("DELETE FROM subject_social_posts WHERE subject_id = ?", (subject_id,))
    
    # Insert mock posts
    for post in mock_posts:
        post_id = str(uuid.uuid4())
        cursor.execute(
            """INSERT INTO subject_social_posts 
            (id, subject_id, feed_id, content, platform, posted_at, scraped_at, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (post_id, subject_id, feed_id, post["content"], post["platform"], 
             post["posted_at"], datetime.now().isoformat(), 
             f"https://{post['platform'].lower()}.com/post/{post_id}")
        )
    
    conn.commit()
    conn.close()
    
    print(f"✅ Added {len(mock_posts)} mock social media posts for Sarah Thompson")
    print(f"   Subject ID: {subject_id}")
    print(f"   These posts show patterns of:")
    print(f"   - Strong online community attachment")
    print(f"   - Skepticism toward mainstream institutions")
    print(f"   - Isolation from offline relationships")
    print(f"   - Attraction to alternative worldviews")
    print(f"\n   Digital clone can now be trained on this data!")

if __name__ == "__main__":
    add_mock_posts()
