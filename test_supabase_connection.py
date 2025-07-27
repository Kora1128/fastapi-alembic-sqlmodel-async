#!/usr/bin/env python3
"""
Test script to verify Supabase configuration
Run this script to test your Supabase database connection
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "backend" / "app"))

try:
    from app.core.config import settings
    from app.db.session import engine
    from sqlalchemy import text
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


async def test_database_connection():
    """Test the database connection"""
    print("Testing Supabase database connection...")
    print(f"Database URI: {str(settings.ASYNC_DATABASE_URI)}")
    
    try:
        async with engine.connect() as connection:
            # Test basic connection
            result = await connection.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connection successful!")
            print(f"PostgreSQL version: {version}")
            
            # Test if we can create a simple table
            await connection.execute(text("""
                CREATE TABLE IF NOT EXISTS supabase_test (
                    id SERIAL PRIMARY KEY,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """))
            
            # Insert a test record
            await connection.execute(text("""
                INSERT INTO supabase_test (message) 
                VALUES ('Supabase connection test successful!')
            """))
            
            # Query the test record
            result = await connection.execute(text("""
                SELECT message, created_at FROM supabase_test 
                ORDER BY created_at DESC LIMIT 1
            """))
            row = result.fetchone()
            if row:
                print(f"✅ Test record: {row.message} at {row.created_at}")
            
            # Clean up
            await connection.execute(text("DROP TABLE supabase_test"))
            await connection.commit()
            
            print("✅ All tests passed! Supabase is configured correctly.")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check your .env file has correct Supabase credentials")
        print("2. Verify your Supabase project is running")
        print("3. Check your network connection")
        return False
    
    return True


async def test_celery_database():
    """Test Celery database connection"""
    print("\nTesting Celery database connection...")
    print(f"Celery DB URI: {str(settings.SYNC_CELERY_BEAT_DATABASE_URI)}")
    
    # For Celery, we test the async connection since we're in an async context
    try:
        from app.db.session import engine_celery
        async with engine_celery.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            print("✅ Celery database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Celery database connection failed: {e}")
        return False


def main():
    """Main test function"""
    print("Supabase Configuration Test")
    print("=" * 40)
    
    # Check environment variables
    print("Environment variables:")
    print(f"DATABASE_HOST: {getattr(settings, 'DATABASE_HOST', 'Not set')}")
    print(f"DATABASE_NAME: {getattr(settings, 'DATABASE_NAME', 'Not set')}")
    print(f"DATABASE_USER: {getattr(settings, 'DATABASE_USER', 'Not set')}")
    print(f"SUPABASE_DATABASE_URL: {getattr(settings, 'SUPABASE_DATABASE_URL', 'Not set')}")
    print()
    
    # Run async tests
    success = asyncio.run(test_database_connection())
    celery_success = asyncio.run(test_celery_database())
    
    if success and celery_success:
        print("\n🎉 All tests passed! Your Supabase configuration is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check your configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main()