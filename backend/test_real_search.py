import requests
from bs4 import BeautifulSoup
import random

def search_duckduckgo(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    # Search for reddit posts matching the query
    search_term = f'site:reddit.com "{query}" (lonely OR depressed OR "need help" OR vent)'
    url = f"https://html.duckduckgo.com/html/?q={search_term}"
    
    try:
        print(f"Searching: {url}")
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        for result in soup.find_all('div', class_='result'):
            title_tag = result.find('a', class_='result__a')
            snippet_tag = result.find('a', class_='result__snippet')
            
            if title_tag and snippet_tag:
                title = title_tag.text
                snippet = snippet_tag.text
                link = title_tag['href']
                
                # Extract a fake username from the title or just randomize
                username = "reddit_user_" + str(random.randint(1000, 9999))
                if " by " in title:
                    try:
                        username = title.split(" by ")[1].split(" ")[0]
                    except:
                        pass
                
                results.append({
                    "username": username,
                    "platform": "Reddit",
                    "sample_post": f"{title}: {snippet[:100]}...",
                    "risk_indicators": ["potential_risk"],
                    "url": link
                })
                
        return results[:5]
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    results = search_duckduckgo("depression")
    print(f"Found {len(results)} results:")
    for r in results:
        print(r)
