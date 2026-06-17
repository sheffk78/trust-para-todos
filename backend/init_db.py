"""
Trust Para Todos — Database Initialization Script.
Run this once to create all tables:  python init_db.py
In production, use Alembic for migrations.
"""
from __future__ import annotations
import asyncio
from database import Base, engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_db")

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ All tables created successfully.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init())