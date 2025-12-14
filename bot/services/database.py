import asyncpg
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone, timedelta
from models import User, Word, Stat, Base
from infrastructure.config import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Database:
    def __init__(self):
        self.pool = None
        self.session = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            host=DB_HOST,
            port=DB_PORT,
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self):
        await self.pool.close()

    async def get_db(self):
        if not self.session:
            self.session = AsyncSessionLocal()
        return self.session

    async def add_user(self, user_id: int, username: str):
        async with self.get_db() as session:
            new_user = User(user_id=user_id, username=username)
            session.add(new_user)
            await session.commit()

    async def get_user(self, user_id: int):
        async with self.get_db() as session:
            result = await session.execute(select(User).filter(User.user_id == user_id))
            return result.scalars().first()

    async def get_all_users(self):
        async with self.get_db() as session:
            result = await session.execute(select(User))
            return result.scalars().all()

    async def get_user_words(self, user_id: int):
        async with self.get_db() as session:
            result = await session.execute(select(Word).filter(Word.user_id == user_id))
            return result.scalars().all()

    # Обновление настроек пользователя и слов
    async def update_word_next_repeat(self, user_id: int, word_id: int, next_repeat=None):
        if next_repeat is None:
            next_repeat = datetime.now(timezone.utc) + timedelta(days=1)
        async with self.get_db() as session:
            word = await session.get(Word, word_id)
            if word and word.user_id == user_id:
                word.next_repeat = next_repeat
                await session.commit()

    async def update_user_setting(self, user_id: int, key: str, value):
        async with self.get_db() as session:
            user = await session.get(User, user_id)
            if user:
                user.settings[key] = value
                await session.commit()



