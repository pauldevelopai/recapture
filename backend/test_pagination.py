import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

from backend.listening_service import listening_service

def test_pagination():
    # Test Page 1
    result = listening_service.get_latest_results(page=1, page_size=5)
    print(f"Page 1: {len(result['items'])} items")
    print(f"Total: {result['total']}")
    print(f"Total Pages: {result['total_pages']}")
    print(f"First Item ID: {result['items'][0].id if result['items'] else 'None'}")

    # Test Page 2
    result2 = listening_service.get_latest_results(page=2, page_size=5)
    print(f"Page 2: {len(result2['items'])} items")
    print(f"First Item ID: {result2['items'][0].id if result2['items'] else 'None'}")

if __name__ == "__main__":
    test_pagination()
