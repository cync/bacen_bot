#!/usr/bin/env python3
"""
Test script to verify database connection and schema initialization
"""
import os
from dotenv import load_dotenv
from storage import get_store

def test_database_connection():
    """Test the database connection and schema initialization"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Check if DATABASE_URL is set
        if not os.getenv("DATABASE_URL"):
            print("❌ DATABASE_URL environment variable not found!")
            print("Please set DATABASE_URL in your environment or .env file")
            return False
        
        print("🔗 Testing database connection...")
        
        # Initialize store (this will create the connection and schema)
        store = get_store()
        
        print("✅ Database connection successful!")
        print("✅ Schema initialized successfully!")
        
        # Test basic operations
        print("🧪 Testing basic operations...")
        
        # Test subscriber operations
        test_chat_id = 123456789
        store.upsert_subscriber(test_chat_id, "Test User", "testuser")
        print("✅ Subscriber upsert test passed")
        
        subscribers = store.list_subscribers()
        print(f"✅ List subscribers test passed (found {len(subscribers)} subscribers)")
        
        # Test seen items operations
        test_source = "test_feed"
        test_item_id = "test_item_123"
        is_new = store.mark_new_and_return_is_new(test_source, test_item_id)
        print(f"✅ Mark new item test passed (is_new: {is_new})")
        
        # Clean up test data
        store.remove_subscriber(test_chat_id)
        print("✅ Cleanup completed")
        
        print("\n🎉 All tests passed! Your database is ready to use.")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    test_database_connection()
