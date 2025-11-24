import asyncio
import uuid
from datetime import datetime
from .pipeline_service import add_source, get_sources, add_raw_content, get_raw_content, approve_content
from .models import Source, RawContent

async def verify_persistence():
    print("--- Verifying Pipeline Data Persistence ---")
    
    # 1. Test Source Persistence
    print("\n1. Testing Source Persistence...")
    test_source = Source(
        id=str(uuid.uuid4()),
        name="Test Persistence Source",
        url="http://test-persistence.com",
        type="direct",
        status="active"
    )
    await add_source(test_source)
    
    sources = await get_sources()
    found_source = next((s for s in sources if s.id == test_source.id), None)
    
    if found_source:
        print(f"✅ Source saved and retrieved: {found_source.name}")
    else:
        print("❌ Source NOT found in DB!")
        return

    # 2. Test Content Persistence
    print("\n2. Testing Content Persistence...")
    test_content = RawContent(
        id=str(uuid.uuid4()),
        source_id=test_source.id,
        content="This is persistent content.",
        url="http://test-persistence.com/article",
        timestamp=datetime.now().isoformat(),
        status="pending",
        risk_score=0.5
    )
    await add_raw_content(test_content)
    
    contents = await get_raw_content()
    found_content = next((c for c in contents if c.id == test_content.id), None)
    
    if found_content:
        print(f"✅ Content saved and retrieved: {found_content.content}")
    else:
        print("❌ Content NOT found in DB!")
        return

    # 3. Test Status Update
    print("\n3. Testing Status Update (Approve)...")
    await approve_content(test_content.id)
    
    contents = await get_raw_content()
    updated_content = next((c for c in contents if c.id == test_content.id), None)
    
    if updated_content and updated_content.status == "approved":
        print(f"✅ Content status updated to: {updated_content.status}")
    else:
        print(f"❌ Content status NOT updated! Found: {updated_content.status if updated_content else 'None'}")

if __name__ == "__main__":
    asyncio.run(verify_persistence())
