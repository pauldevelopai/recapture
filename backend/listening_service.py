import asyncio
import random
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from .models import ListeningResult, DisinformationTrend
from .trend_monitor import get_active_trends
from .connectors import RedditConnector, FourChanConnector
from .database import get_db_connection

class ListeningService:
    def __init__(self):
        self.connectors = [
            # Monitoring subreddits known for potential radicalization vectors or harmful ideologies
            RedditConnector(subreddits=["TheRedPill", "MensRights", "Antifeminists", "PurplePillDebate", "4chan", "greentext"]),
            FourChanConnector(boards=["pol", "b", "r9k", "x"])
        ]
        # self.results removed in favor of DB
        self.max_history = 200 # Still useful for limiting DB query or cleanup
        self._task = None
        self.running = False
        self.trends: List[DisinformationTrend] = []

    async def start_listening(self):
        if self.running:
            return
        
        self.running = True
        self.trends = await get_active_trends()
        self._task = asyncio.create_task(self._listen_loop())
        print("Real Listening Service Started")

    async def stop_listening(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        print("Listening Service Stopped")

    def is_running(self) -> bool:
        return self.running

    async def _listen_loop(self):
        while self.running:
            try:
                print("Fetching new posts from real sources...")
                all_posts = []
                
                # Fetch from all connectors
                for connector in self.connectors:
                    if not self.running: break
                    posts = await asyncio.to_thread(connector.fetch_posts, limit=20)
                    all_posts.extend(posts)
                
                # Process and Match
                new_results_count = 0
                conn = get_db_connection()
                cursor = conn.cursor()
                
                for post in all_posts:
                    # Check if already exists in DB (deduplication)
                    cursor.execute("SELECT id FROM listening_results WHERE id = ?", (post['id'],))
                    if cursor.fetchone():
                        continue
                        
                    matched_trend = self._match_trends(post['content'])
                    
                    # Create result object
                    result = ListeningResult(
                        id=post['id'],
                        source_platform=post['platform'],
                        author=post['author'],
                        content=post['content'][:500] + ("..." if len(post['content']) > 500 else ""), # Truncate for display
                        timestamp=post['timestamp'],
                        matched_trend_id=matched_trend.id if matched_trend else None,
                        matched_trend_topic=matched_trend.topic if matched_trend else None,
                        severity=matched_trend.severity if matched_trend else "Low",
                        url=post['url']
                    )
                    
                    # Insert into DB
                    cursor.execute(
                        "INSERT INTO listening_results (id, source_platform, author, content, timestamp, matched_trend_id, matched_trend_topic, severity, url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (result.id, result.source_platform, result.author, result.content, result.timestamp, result.matched_trend_id, result.matched_trend_topic, result.severity, result.url)
                    )
                    new_results_count += 1
                
                conn.commit()
                conn.close()
                
                print(f"Processed {new_results_count} new unique posts.")
                
                # Optional: Cleanup old results to keep DB size manageable
                # self._cleanup_old_results()

            except Exception as e:
                print(f"Error in listening loop: {e}")

            # Wait before next poll (avoid rate limits)
            await asyncio.sleep(30) 

    def _match_trends(self, content: str) -> Optional[DisinformationTrend]:
        """
        Simple keyword matching against active trends.
        """
        content_lower = content.lower()
        for trend in self.trends:
            # Check common phrases
            for phrase in trend.common_phrases:
                if phrase.lower() in content_lower:
                    return trend
        return None

    def get_latest_results(self, limit: int = 50) -> List[ListeningResult]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM listening_results ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append(ListeningResult(
                id=row['id'],
                source_platform=row['source_platform'],
                author=row['author'],
                content=row['content'],
                timestamp=row['timestamp'],
                matched_trend_id=row['matched_trend_id'],
                matched_trend_topic=row['matched_trend_topic'],
                severity=row['severity'],
                url=row['url']
            ))
        return results

# Global instance
listening_service = ListeningService()
