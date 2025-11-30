import asyncio
import os
import sys
from sqlalchemy import text

# Add the parent directory to sys.path to allow importing from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine

async def clear_data():
    print("Clearing all project data...")
    try:
        async with engine.begin() as conn:
            # Disable triggers temporarily to avoid foreign key issues if needed, 
            # but CASCADE should handle it.
            
            # Truncate tables
            print("Truncating tasks...")
            await conn.execute(text("TRUNCATE TABLE tasks CASCADE;"))
            
            print("Truncating sprints...")
            await conn.execute(text("TRUNCATE TABLE sprints CASCADE;"))
            
            print("Truncating projects...")
            await conn.execute(text("TRUNCATE TABLE projects CASCADE;"))
            
            # Note: Not deleting users as they might be needed for login/auth
            
        print("✅ All projects, tasks, and sprints have been deleted.")
    except Exception as e:
        print(f"❌ Error clearing data: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(clear_data())
