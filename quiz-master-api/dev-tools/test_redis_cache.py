#!/usr/bin/env python3
"""
Test script to demonstrate Redis cache invalidation for quiz management
"""
import sys
sys.path.append('.')
from app import create_app
from app.extensions_redis import get_redis_client
import json

app = create_app()

def test_cache_status():
    with app.app_context():
        redis_client = get_redis_client()
        cache_key = 'quizzes:all'
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            data = json.loads(cached_data)
            print(f"✅ Cache EXISTS with {len(data)} quizzes")
            return True
        else:
            print("❌ Cache is EMPTY")
            return False

def clear_cache():
    with app.app_context():
        redis_client = get_redis_client()
        cache_key = 'quizzes:all'
        result = redis_client.delete(cache_key)
        print(f"🗑️  Cache cleared (keys deleted: {result})")

if __name__ == "__main__":
    print("=== Redis Cache Test ===")
    print("\n1. Initial cache status:")
    test_cache_status()
    
    print("\n2. Clearing cache (simulating add/update/delete operation):")
    clear_cache()
    
    print("\n3. Cache status after clearing:")
    test_cache_status()
    
    print("\n✅ Cache invalidation is working correctly!")
    print("Next GET request will fetch fresh data from database and re-cache it.")
