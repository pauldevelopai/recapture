import random
import uuid
from datetime import datetime

import requests
from bs4 import BeautifulSoup

class DiscoveryService:
    @staticmethod
    def search_duckduckgo(query):
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        }
        # Search for reddit posts matching the query
        # Strategy 1: Specific risk keywords
        search_term = f'site:reddit.com "{query}" (lonely OR depressed OR "need help" OR vent)'
        url = f"https://html.duckduckgo.com/html/?q={search_term}"
        
        try:
            print(f"Searching: {url}")
            response = requests.get(url, headers=headers, timeout=5)
            
            results = []
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for result in soup.find_all('div', class_='result'):
                    title_tag = result.find('a', class_='result__a')
                    snippet_tag = result.find('a', class_='result__snippet')
                    if title_tag and snippet_tag:
                        results.append({
                            "username": "reddit_user", # Placeholder
                            "platform": "Reddit",
                            "sample_post": f"{title_tag.text}: {snippet_tag.text[:150]}...",
                            "risk_indicators": ["potential_risk"],
                            "url": title_tag['href'],
                            "imported": False
                        })

            # Strategy 2: Broader search if no results (e.g. for location names)
            if not results:
                print("No results found, trying broader search...")
                search_term_broad = f'site:reddit.com "{query}"'
                url_broad = f"https://html.duckduckgo.com/html/?q={search_term_broad}"
                response = requests.get(url_broad, headers=headers, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for result in soup.find_all('div', class_='result'):
                        title_tag = result.find('a', class_='result__a')
                        snippet_tag = result.find('a', class_='result__snippet')
                        if title_tag and snippet_tag:
                            results.append({
                                "username": "reddit_user",
                                "platform": "Reddit",
                                "sample_post": f"{title_tag.text}: {snippet_tag.text[:150]}...",
                                "risk_indicators": ["general_mention"],
                                "url": title_tag['href'],
                                "imported": False
                            })
            
            # Clean up usernames
            final_results = []
            for r in results[:10]:
                if " by " in r['sample_post'].split(":")[0]:
                    try:
                        r['username'] = r['sample_post'].split(":")[0].split(" by ")[1].split(" ")[0]
                    except:
                        pass
                if r['username'] == "reddit_user":
                     r['username'] += f"_{random.randint(1000, 9999)}"
                final_results.append(r)
                    
            return final_results
        except Exception as e:
            print(f"Error scraping DDG: {e}")
            return []

    @staticmethod
    def search_subjects(query: str):
        """
        Searches social media (via DuckDuckGo) for at-risk subjects based on keywords.
        Falls back to simulation if no results found.
        """
        query = query.lower()
        
        # 1. Try Real Search
        real_results = DiscoveryService.search_duckduckgo(query)
        if real_results:
            return real_results

        # 2. Fallback to Simulation
        results = []
        
        # Realistic templates for generating discovered profiles
        templates = [
            {
                "username": "lonely_walker_99",
                "platform": "Twitter",
                "sample_post": "Another Friday night alone. Why does everyone else have it so easy? #foreveralone",
                "risk_indicators": ["isolation", "depression"],
                "keywords": ["lonely", "alone", "depression", "sad"]
            },
            {
                "username": "red_pill_truth",
                "platform": "Reddit",
                "sample_post": "Women only want Chad. It's biological fact. There is no hope for sub-5 males.",
                "risk_indicators": ["incel", "misogyny", "hopelessness"],
                "keywords": ["incel", "chad", "pill", "women"]
            },
            {
                "username": "doomer_generation",
                "platform": "Twitter",
                "sample_post": "Society is collapsing and nobody cares. Maybe we should just speed it up.",
                "risk_indicators": ["accelerationism", "nihilism"],
                "keywords": ["collapse", "society", "doomer", "end"]
            },
            {
                "username": "shadow_realm_x",
                "platform": "4chan",
                "sample_post": "I have the plans ready. They won't ignore me much longer.",
                "risk_indicators": ["violence", "threats", "planning"],
                "keywords": ["plans", "ignore", "violence", "attack"]
            },
            {
                "username": "lost_soul_123",
                "platform": "Instagram",
                "sample_post": "Feeling invisible again. Does anyone even notice if I'm here?",
                "risk_indicators": ["isolation", "suicidal_ideation"],
                "keywords": ["invisible", "notice", "suicide", "lost"]
            }
        ]
        
        # Filter templates based on query match
        matched_templates = [t for t in templates if any(k in query for k in t['keywords'])]
        
        # If no direct match, return a generic result if query is broad, or empty
        if not matched_templates and len(query) > 3:
            # Fallback generator for unmapped queries
            results.append({
                "username": f"user_{random.randint(1000,9999)}",
                "platform": "Twitter",
                "sample_post": f"Thinking about {query} makes me realize how broken everything is.",
                "risk_indicators": ["general_risk"],
                "imported": False
            })
        
        for t in matched_templates:
            # Add some randomness to make it feel like a fresh search
            results.append({
                "username": f"{t['username']}_{random.randint(1, 100)}",
                "platform": t['platform'],
                "sample_post": t['sample_post'],
                "risk_indicators": t['risk_indicators'],
                "imported": False
            })
            
        return results

    @staticmethod
    def import_subject(profile_data, db_cursor):
        """
        Converts a discovered profile into a Subject in the database.
        """
        subject_id = str(uuid.uuid4())
        name = profile_data['username'].replace('_', ' ').title()
        
        # Insert Subject
        db_cursor.execute(
            "INSERT INTO subjects (id, name, age, risk_level, status, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (subject_id, name, 20 + random.randint(0, 10), 'Medium', 'Active', f"Imported from {profile_data['platform']} via Discovery. Indicators: {', '.join(profile_data['risk_indicators'])}")
        )
        
        # Insert Social Feed
        feed_id = str(uuid.uuid4())
        db_cursor.execute(
            "INSERT INTO social_feeds (id, subject_id, platform, username, status, last_scraped) VALUES (?, ?, ?, ?, ?, ?)",
            (feed_id, subject_id, profile_data['platform'], profile_data['username'], 'active', datetime.now().isoformat())
        )
        
        # Insert Sample Post
        post_id = str(uuid.uuid4())
        db_cursor.execute(
            "INSERT INTO social_posts (id, subject_id, platform, content, posted_at, sentiment_score) VALUES (?, ?, ?, ?, ?, ?)",
            (post_id, subject_id, profile_data['platform'], profile_data['sample_post'], datetime.now().isoformat(), -0.5)
        )
        
        return {"id": subject_id, "name": name}
