"""Database connection and session management"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Replace 'postgresql://' with 'postgresql+asyncpg://' for async operations
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    # Remove all query parameters and convert to asyncpg
    base_url = DATABASE_URL.split("?")[0]
    DATABASE_URL = base_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async engine with SSL via connect_args
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={
        "ssl": "require"
    }
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base for models
Base = declarative_base()

async def get_db():
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
