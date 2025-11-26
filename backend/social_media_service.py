from typing import List, Dict, Optional
import os
import json
import uuid
from datetime import datetime
from .database import get_db_connection
from .models import SocialMediaFeed, SubjectSocialPost

# Environment variables for API credentials
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")


class TwitterClient:
    """Client for Twitter API v2"""
    
    def __init__(self):
        self.bearer_token = TWITTER_BEARER_TOKEN
        self.available = bool(self.bearer_token)
    
    async def fetch_user_tweets(self, username: str, max_results: int = 100) -> List[Dict]:
        """Fetch recent tweets from a user"""
        if not self.available:
            raise Exception("Twitter API credentials not configured")
        
        try:
            import tweepy
            
            client = tweepy.Client(bearer_token=self.bearer_token)
            
            # Get user ID from username
            user = client.get_user(username=username)
            if not user.data:
                return []
            
            # Fetch tweets
            tweets = client.get_users_tweets(
                id=user.data.id,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'entities']
            )
            
            if not tweets.data:
                return []
            
            posts = []
            for tweet in tweets.data:
                posts.append({
                    'content': tweet.text,
                    'posted_at': tweet.created_at.isoformat() if tweet.created_at else None,
                    'url': f"https://twitter.com/{username}/status/{tweet.id}",
                    'engagement_metrics': {
                        'likes': tweet.public_metrics.get('like_count', 0),
                        'retweets': tweet.public_metrics.get('retweet_count', 0),
                        'replies': tweet.public_metrics.get('reply_count', 0),
                    } if hasattr(tweet, 'public_metrics') else {}
                })
            
            return posts
            
        except Exception as e:
            raise Exception(f"Twitter API error: {str(e)}")


class InstagramClient:
    """Client for Instagram Graph API"""
    
    def __init__(self):
        self.access_token = INSTAGRAM_ACCESS_TOKEN
        self.available = bool(self.access_token)
    
    async def fetch_user_posts(self, username: str, max_results: int = 100) -> List[Dict]:
        """Fetch recent Instagram posts"""
        if not self.available:
            raise Exception("Instagram API credentials not configured")
        
        try:
            import requests
            
            # Note: Instagram Graph API requires user ID, not username
            # This is a simplified implementation - real implementation needs user ID mapping
            base_url = "https://graph.instagram.com/me/media"
            params = {
                'fields': 'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count',
                'access_token': self.access_token,
                'limit': max_results
            }
            
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            posts = []
            for item in data.get('data', []):
                posts.append({
                    'content': item.get('caption', ''),
                    'posted_at': item.get('timestamp'),
                    'url': item.get('permalink'),
                    'engagement_metrics': {
                        'likes': item.get('like_count', 0),
                        'comments': item.get('comments_count', 0),
                    }
                })
            
            return posts
            
        except Exception as e:
            raise Exception(f"Instagram API error: {str(e)}")


class TikTokClient:
    """Client for TikTok API"""
    
    def __init__(self):
        self.client_key = TIKTOK_CLIENT_KEY
        self.client_secret = TIKTOK_CLIENT_SECRET
        self.available = bool(self.client_key and self.client_secret)
    
    async def fetch_user_videos(self, username: str, max_results: int = 100) -> List[Dict]:
        """Fetch recent TikTok videos"""
        if not self.available:
            raise Exception("TikTok API credentials not configured")
        
        try:
            # TikTok API implementation would go here
            # This is a placeholder as TikTok's official API has limited access
            raise Exception("TikTok API integration requires business account and approval")
            
        except Exception as e:
            raise Exception(f"TikTok API error: {str(e)}")


class FacebookClient:
    """Client for Facebook Graph API"""
    
    def __init__(self):
        self.access_token = FACEBOOK_ACCESS_TOKEN
        self.available = bool(self.access_token)
    
    async def fetch_user_posts(self, user_id: str, max_results: int = 100) -> List[Dict]:
        """Fetch recent Facebook posts"""
        if not self.available:
            raise Exception("Facebook API credentials not configured")
        
        try:
            import requests
            
            base_url = f"https://graph.facebook.com/v18.0/{user_id}/posts"
            params = {
                'fields': 'id,message,created_time,permalink_url,likes.summary(true),comments.summary(true)',
                'access_token': self.access_token,
                'limit': max_results
            }
            
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            posts = []
            for item in data.get('data', []):
                posts.append({
                    'content': item.get('message', ''),
                    'posted_at': item.get('created_time'),
                    'url': item.get('permalink_url'),
                    'engagement_metrics': {
                        'likes': item.get('likes', {}).get('summary', {}).get('total_count', 0),
                        'comments': item.get('comments', {}).get('summary', {}).get('total_count', 0),
                    }
                })
            
            return posts
            
        except Exception as e:
            raise Exception(f"Facebook API error: {str(e)}")


# Platform client registry
PLATFORM_CLIENTS = {
    'twitter': TwitterClient,
    'instagram': InstagramClient,
    'tiktok': TikTokClient,
    'facebook': FacebookClient,
}


async def scrape_feed(feed: SocialMediaFeed) -> tuple[List[SubjectSocialPost], Optional[str]]:
    """
    Scrape a single social media feed and return posts
    Returns: (list of posts, error_message if any)
    """
    platform = feed.platform.lower()
    
    if platform not in PLATFORM_CLIENTS:
        return [], f"Unsupported platform: {feed.platform}"
    
    client_class = PLATFORM_CLIENTS[platform]
    client = client_class()
    
    if not client.available:
        return [], f"{feed.platform} API credentials not configured"
    
    try:
        # Fetch posts from the platform
        if platform == 'twitter':
            raw_posts = await client.fetch_user_tweets(feed.username or feed.profile_url.split('/')[-1])
        elif platform == 'instagram':
            raw_posts = await client.fetch_user_posts(feed.username or feed.profile_url.split('/')[-1])
        elif platform == 'tiktok':
            raw_posts = await client.fetch_user_videos(feed.username or feed.profile_url.split('/')[-1])
        elif platform == 'facebook':
            raw_posts = await client.fetch_user_posts(feed.username or feed.profile_url.split('/')[-1])
        else:
            return [], f"Unknown platform: {platform}"
        
        # Convert to SubjectSocialPost objects
        posts = []
        now = datetime.now().isoformat()
        
        for raw_post in raw_posts:
            post = SubjectSocialPost(
                id=str(uuid.uuid4()),
                subject_id=feed.subject_id,
                feed_id=feed.id,
                content=raw_post.get('content', ''),
                posted_at=raw_post.get('posted_at'),
                platform=feed.platform,
                url=raw_post.get('url'),
                engagement_metrics=raw_post.get('engagement_metrics', {}),
                scraped_at=now
            )
            posts.append(post)
        
        return posts, None
        
    except Exception as e:
        return [], str(e)


async def save_social_posts(posts: List[SubjectSocialPost]):
    """Save social media posts to database"""
    if not posts:
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for post in posts:
        # Check if post already exists (by URL or content+date to avoid duplicates)
        if post.url:
            cursor.execute(
                "SELECT id FROM subject_social_posts WHERE url = ?",
                (post.url,)
            )
            if cursor.fetchone():
                continue  # Skip duplicate
        
        cursor.execute(
            """INSERT INTO subject_social_posts 
            (id, subject_id, feed_id, content, posted_at, platform, url, engagement_metrics, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                post.id,
                post.subject_id,
                post.feed_id,
                post.content,
                post.posted_at,
                post.platform,
                post.url,
                json.dumps(post.engagement_metrics) if post.engagement_metrics else None,
                post.scraped_at
            )
        )
    
    conn.commit()
    conn.close()


async def scrape_subject_feeds(subject_id: str) -> Dict:
    """
    Scrape all social media feeds for a subject
    Returns summary of results
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all feeds for this subject
    cursor.execute(
        "SELECT * FROM social_media_feeds WHERE subject_id = ? AND status = 'active'",
        (subject_id,)
    )
    feeds = cursor.fetchall()
    conn.close()
    
    if not feeds:
        return {
            'success': False,
            'message': 'No active social media feeds found for this subject'
        }
    
    total_posts = 0
    results = []
    
    for feed_row in feeds:
        feed = SocialMediaFeed(
            id=feed_row['id'],
            subject_id=feed_row['subject_id'],
            platform=feed_row['platform'],
            username=feed_row['username'],
            profile_url=feed_row['profile_url'],
            status=feed_row['status']
        )
        
        posts, error = await scrape_feed(feed)
        
        # Update feed status
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if error:
            cursor.execute(
                "UPDATE social_media_feeds SET error_message = ?, status = 'error' WHERE id = ?",
                (error, feed.id)
            )
            results.append({
                'platform': feed.platform,
                'success': False,
                'error': error,
                'posts_count': 0
            })
        else:
            await save_social_posts(posts)
            cursor.execute(
                "UPDATE social_media_feeds SET last_scraped = ?, error_message = NULL, status = 'active' WHERE id = ?",
                (datetime.now().isoformat(), feed.id)
            )
            total_posts += len(posts)
            results.append({
                'platform': feed.platform,
                'success': True,
                'posts_count': len(posts)
            })
        
        conn.commit()
        conn.close()
    
    return {
        'success': True,
        'total_posts': total_posts,
        'feeds_scraped': len(feeds),
        'results': results
    }


async def get_subject_posts(subject_id: str, limit: int = 100, offset: int = 0) -> List[SubjectSocialPost]:
    """Get social media posts for a subject"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """SELECT * FROM subject_social_posts 
        WHERE subject_id = ? 
        ORDER BY posted_at DESC 
        LIMIT ? OFFSET ?""",
        (subject_id, limit, offset)
    )
    
    rows = cursor.fetchall()
    conn.close()
    
    posts = []
    for row in rows:
        posts.append(SubjectSocialPost(
            id=row['id'],
            subject_id=row['subject_id'],
            feed_id=row['feed_id'],
            content=row['content'],
            posted_at=row['posted_at'],
            platform=row['platform'],
            url=row['url'],
            engagement_metrics=json.loads(row['engagement_metrics']) if row['engagement_metrics'] else None,
            scraped_at=row['scraped_at']
        ))
    
    return posts
