import requests
import html
import re
from typing import List, Dict, Optional
from datetime import datetime
import time

class SocialConnector:
    def fetch_posts(self, limit: int = 20) -> List[Dict]:
        raise NotImplementedError

class RedditConnector(SocialConnector):
    def __init__(self, subreddits: List[str] = ["all"]):
        self.subreddits = subreddits
        # Reddit requires a custom User-Agent to avoid 429 Too Many Requests
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}

    def fetch_posts(self, limit: int = 25) -> List[Dict]:
        all_posts = []
        for sub in self.subreddits:
            try:
                url = f"https://www.reddit.com/r/{sub}/new.json?limit={limit}"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code != 200:
                    print(f"Failed to fetch Reddit r/{sub}: {response.status_code}")
                    continue

                data = response.json()
                children = data.get('data', {}).get('children', [])
                
                for child in children:
                    post = child['data']
                    all_posts.append({
                        "platform": "Reddit",
                        "author": post.get('author', 'unknown'),
                        "content": f"{post.get('title', '')}\n{post.get('selftext', '')}",
                        "url": f"https://reddit.com{post.get('permalink', '')}",
                        "timestamp": datetime.fromtimestamp(post.get('created_utc', time.time())).isoformat(),
                        "id": f"reddit_{post.get('id')}"
                    })
            except Exception as e:
                print(f"Error fetching Reddit r/{sub}: {e}")
        
        return all_posts

class FourChanConnector(SocialConnector):
    def __init__(self, boards: List[str] = ["pol"]):
        self.boards = boards

    def fetch_posts(self, limit: int = 50) -> List[Dict]:
        all_posts = []
        for board in self.boards:
            try:
                # 4chan catalog gives all threads
                url = f"https://a.4cdn.org/{board}/catalog.json"
                response = requests.get(url, timeout=10)
                
                if response.status_code != 200:
                    print(f"Failed to fetch 4chan /{board}/: {response.status_code}")
                    continue

                pages = response.json()
                
                count = 0
                for page in pages:
                    for thread in page.get('threads', []):
                        if count >= limit:
                            break
                        
                        # Clean HTML tags from comment
                        com = thread.get('com', '')
                        clean_text = re.sub('<[^<]+?>', '', html.unescape(com))
                        
                        # 4chan images
                        img_url = ""
                        if 'tim' in thread and 'ext' in thread:
                            img_url = f"https://i.4cdn.org/{board}/{thread['tim']}{thread['ext']}"

                        all_posts.append({
                            "platform": f"4chan /{board}/",
                            "author": thread.get('name', 'Anonymous'),
                            "content": f"{thread.get('sub', '')}\n{clean_text}",
                            "url": f"https://boards.4chan.org/{board}/thread/{thread.get('no')}",
                            "timestamp": datetime.fromtimestamp(thread.get('time', time.time())).isoformat(),
                            "id": f"4chan_{board}_{thread.get('no')}",
                            "image": img_url
                        })
                        count += 1
            except Exception as e:
                print(f"Error fetching 4chan /{board}/: {e}")
                
        return all_posts
