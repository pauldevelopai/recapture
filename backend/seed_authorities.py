"""
Script to seed authorities for our realistic test subjects.
"""
import uuid
from database import get_db_connection

def seed_authorities():
    print("👥 Seeding authorities for subjects...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get Alex Mercer's ID
    cursor.execute("SELECT id FROM subjects WHERE name = 'Alex Mercer'")
    alex_row = cursor.fetchone()
    if not alex_row:
        print("❌ Alex Mercer not found. Run seed_real_data.py first.")
        return
    alex_id = alex_row['id']
    
    # Get Jordan Lee's ID
    cursor.execute("SELECT id FROM subjects WHERE name = 'Jordan Lee'")
    jordan_row = cursor.fetchone()
    if not jordan_row:
        print("❌ Jordan Lee not found. Run seed_real_data.py first.")
        return
    jordan_id = jordan_row['id']
    
    # Alex's authorities (Incel/Blackpill - needs mental health professional)
    alex_authorities = [
        {
            "id": str(uuid.uuid4()),
            "subject_id": alex_id,
            "name": "Dr. Sarah Chen",
            "role": "Mental Health Professional",
            "relation": "Therapist"
        },
        {
            "id": str(uuid.uuid4()),
            "subject_id": alex_id,
            "name": "Mom",
            "role": "Parent",
            "relation": "Parent"
        },
        {
            "id": str(uuid.uuid4()),
            "subject_id": alex_id,
            "name": "Coach Dan Miller",
            "role": "Coach",
            "relation": "Coach"
        }
    ]
    
    # Jordan's authorities (Accelerationism - needs diverse approach)
    jordan_authorities = [
        {
            "id": str(uuid.uuid4()),
            "subject_id": jordan_id,
            "name": "Officer Martinez",
            "role": "Law Enforcement",
            "relation": "Counselor"
        },
        {
            "id": str(uuid.uuid4()),
            "subject_id": jordan_id,
            "name": "Professor Thompson",
            "role": "Teacher",
            "relation": "Mentor"
        },
        {
            "id": str(uuid.uuid4()),
            "subject_id": jordan_id,
            "name": "Father John",
            "role": "Religious Leader",
            "relation": "Religious Guide"
        }
    ]
    
    all_authorities = alex_authorities + jordan_authorities
    
    for auth in all_authorities:
        cursor.execute(
            "INSERT INTO authorities (id, subject_id, name, role, relation) VALUES (?, ?, ?, ?, ?)",
            (auth['id'], auth['subject_id'], auth['name'], auth['role'], auth['relation'])
        )
    
    conn.commit()
    conn.close()
    
    print(f"✅ Created {len(all_authorities)} authorities")
    print("   - Alex Mercer: Dr. Sarah Chen (Mental Health), Mom (Parent), Coach Dan (Coach)")
    print("   - Jordan Lee: Officer Martinez (Law Enforcement), Professor Thompson (Teacher), Father John (Religious Leader)")

if __name__ == "__main__":
    seed_authorities()
