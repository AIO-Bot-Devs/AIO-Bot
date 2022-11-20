import asyncio

from sqlalchemy import BigInteger, Column, Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Suggestions(Base):
    __tablename__ = "suggestions"
    message_id = Column(BigInteger, primary_key=True, autoincrement=False)
    rating = Column(Integer, nullable=False, unique=False, default=0)


engine = create_async_engine("sqlite+aiosqlite:///suggestions.db")

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # close and clear open connection pools
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
