import asyncio
from discovery_agent import discover_new_sources

async def test_discovery():
    print("Testing Discovery Agent...")
    try:
        results = await discover_new_sources(["latest conspiracy theories"])
        print(f"✅ Found {len(results)} results.")
        if results:
            print(f"   Sample: {results[0]['title']}")
    except Exception as e:
        print(f"❌ Discovery failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_discovery())
