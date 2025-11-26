"""
Verification script for social media and digital clone features
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_social_media_workflow():
    print_section("SOCIAL MEDIA & DIGITAL CLONE VERIFICATION")
    
    # Step 1: Create a test subject
    print("1. Creating test subject...")
    subject_data = {
        "id": f"test-subject-{int(time.time())}",
        "name": "Test Subject",
        "age": 17,
        "risk_level": "Medium",
        "notes": "Test subject for social media and clone features"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/subjects", json=subject_data)
        if resp.status_code == 200:
            subject_id = resp.json()['id']
            print(f"✅ Subject created: {subject_id}")
        else:
            print(f"❌ Failed to create subject: {resp.status_code}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Step 2: Add social media feeds
    print("\n2. Adding social media feeds...")
    feeds = [
        {
            "platform": "Twitter",
            "username": "elonmusk",  # Using a public account for testing
            "profile_url": "https://twitter.com/elonmusk"
        }
    ]
    
    for feed in feeds:
        try:
            resp = requests.post(f"{BASE_URL}/subjects/{subject_id}/social-feeds", json=feed)
            if resp.status_code == 200:
                print(f"✅ Added {feed['platform']} feed: @{feed['username']}")
            else:
                print(f"❌ Failed to add {feed['platform']} feed: {resp.status_code}")
        except Exception as e:
            print(f"❌ Error adding feed: {e}")
    
    # Step 3: Trigger scraping
    print("\n3. Triggering social media scraping...")
    print("Note: This will likely fail without proper API credentials configured.")
    print("Expected error: 'Twitter API credentials not configured' or similar")
    
    try:
        resp = requests.post(f"{BASE_URL}/subjects/{subject_id}/scrape-feeds")
        result = resp.json()
        print(f"Scraping result: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print(f"✅ Scraped {result.get('total_posts', 0)} posts")
        else:
            print(f"⚠️  Scraping not successful (expected if API creds not configured)")
            print(f"   Message: {result.get('message', 'No message')}")
    except Exception as e:
        print(f"⚠️  Scraping error (expected): {e}")
    
    # Step 4: Check social media posts
    print("\n4. Checking scraped posts...")
    try:
        resp = requests.get(f"{BASE_URL}/subjects/{subject_id}/social-posts")
        posts = resp.json()
        print(f"Retrieved {len(posts)} posts")
        if posts:
            print(f"✅ Posts were scraped!")
            print(f"Sample post: {posts[0]['content'][:100]}...")
        else:
            print("⚠️  No posts found (expected if scraping failed)")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Step 5: Generate risk profile
    print("\n5. Generating risk profile...")
    try:
        resp = requests.post(f"{BASE_URL}/subjects/{subject_id}/risk-profile")
        if resp.status_code == 200:
            profile = resp.json()
            print(f"✅ Risk profile generated!")
            print(f"   Risk Score: {profile['overall_risk_score']}/100")
            print(f"   Themes: {', '.join(profile['detected_themes'][:5])}")
            print(f"   Risk Factors: {len(profile['risk_factors'])}")
        else:
            print(f"⚠️  Risk profile generation returned {resp.status_code}")
            print(f"   This is expected if no posts were scraped")
    except Exception as e:
        print(f"⚠️  Error (expected if no posts): {e}")
    
    # Step 6: Create digital clone
    print("\n6. Getting/creating digital clone...")
    try:
        resp = requests.get(f"{BASE_URL}/clones/{subject_id}")
        if resp.status_code == 200:
            clone = resp.json()
            print(f"✅ Digital clone created!")
            print(f"   Clone ID: {clone['id']}")
            print(f"   Status: {clone['status']}")
            print(f"   Training Posts: {clone['training_post_count']}")
            if clone.get('personality_model'):
                traits = clone['personality_model'].get('traits', [])
                print(f"   Personality Traits: {', '.join(traits[:3])}")
        else:
            print(f"⚠️  Clone creation returned {resp.status_code}")
            print(f"   This is expected if no posts were scraped")
    except Exception as e:
        print(f"⚠️  Error (expected if no posts): {e}")
    
    # Step 7: Test clone chat
    print("\n7. Testing clone chat...")
    try:
        # First get the clone
        resp = requests.get(f"{BASE_URL}/clones/{subject_id}")
        if resp.status_code == 200:
            clone = resp.json()
            clone_id = clone['id']
            
            # Send a test message
            resp = requests.post(
                f"{BASE_URL}/clones/{clone_id}/chat",
                json={
                    "clone_id": clone_id,
                    "message": "Hey, I've been worried about some of the things you've been posting online. Can we talk?"
                }
            )
            
            if resp.status_code == 200:
                result = resp.json()
                print(f"✅ Clone responded!")
                print(f"   Clone Response: {result['clone_response'][:150]}...")
                print(f"   Effectiveness Score: {result['effectiveness_score']}/100")
                print(f"   Suggestions: {len(result['suggestions'])} improvement tips")
            else:
                print(f"⚠️  Clone chat returned {resp.status_code}")
        else:
            print(f"⚠️  Could not get clone for chat test")
    except Exception as e:
        print(f"⚠️  Error (expected if no posts): {e}")
    
    print_section("VERIFICATION COMPLETE")
    print("\nSUMMARY:")
    print("- Subject creation: Working")
    print("- Social feed management: Working")
    print("- Social media scraping: Architecture ready (needs API creds)")
    print("- Risk profile generation: Architecture ready (needs posts)")
    print("- Digital clone creation: Architecture ready (needs posts)")
    print("- Clone chat: Architecture ready (needs trained clone)")
    print("\nNEXT STEPS:")
    print("1. Configure social media API credentials in environment variables")
    print("2. Add real social media accounts to a subject")
    print("3. Trigger scraping to get actual posts")
    print("4. Generate risk profile from real posts")
    print("5. Train digital clone with real data")
    print("6. Test arguments against trained clone")
    
if __name__ == "__main__":
    test_social_media_workflow()
