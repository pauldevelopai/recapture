import asyncio
from connectors import RedditConnector, FourChanConnector

async def test_connectors():
    print("Testing Reddit Connector...")
    reddit = RedditConnector(subreddits=["all"])
    posts = reddit.fetch_posts(limit=5)
    print(f"✅ Fetched {len(posts)} Reddit posts.")
    if posts:
        print(f"   Sample: {posts[0]['content'][:100]}...")

    print("\nTesting 4chan Connector...")
    fourchan = FourChanConnector(boards=["pol"])
    posts = fourchan.fetch_posts(limit=5)
    print(f"✅ Fetched {len(posts)} 4chan posts.")
    if posts:
        print(f"   Sample: {posts[0]['content'][:100]}...")

if __name__ == "__main__":
    asyncio.run(test_connectors())
