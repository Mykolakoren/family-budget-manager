from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings

# Sync database setup
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async database setup (for future use with async operations)
if "sqlite" in settings.DATABASE_URL:
    async_database_url = settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
else:
    async_database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async_engine = create_async_engine(async_database_url)
AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """Dependency to get async database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def create_tables():
    """Create database tables."""
    from app.models import user, account, category, transaction, budget
    
    if "sqlite" not in settings.DATABASE_URL:
        # For PostgreSQL, use async
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    else:
        # For SQLite, use sync
        Base.metadata.create_all(bind=engine)