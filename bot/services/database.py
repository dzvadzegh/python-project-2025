from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import (
    Table,
    MetaData,
    Column,
    Integer,
    String,
    DateTime,
    Float,
    JSON,
    insert,
    update,
    select,
)
from sqlalchemy.dialects.postgresql import JSONB, insert as pg_insert
from datetime import datetime, timezone, timedelta

from bot.infrastructure.config import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT
from bot.models.user import User
from bot.models.stats import Stats
from bot.models.word import Word


DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("user_id", Integer, primary_key=True),
    Column("username", String),
    Column("settings", JSONB, default=dict),
    Column("progress", JSONB, default=dict),
    Column("words_added", JSONB, default=dict),
    Column(
        "last_active",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    ),
    Column("ml_profile", JSONB, default=dict),
)

words = Table(
    "words",
    metadata,
    Column("word_id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer),
    Column("text", String),
    Column("translation", String),
    Column("next_repeat", DateTime(timezone=True)),
    Column("repeat_count", Integer, default=0),
    Column(
        "created_at",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    ),
    Column("base_difficulty", Float, default=0.5),
    Column("personal_difficulty", Float, default=0.5),
    Column("difficulty", Float, default=0.5),
    Column("stability", Float, default=1.0),
    Column("ml_score", Float, default=0.5),
    Column("history", JSONB, default=list),
)

stats = Table(
    "stats",
    metadata,
    Column("user_id", Integer, primary_key=True),
    Column("learned_words", Integer, default=0),
    Column("success_rate", Float, default=0.0),
    Column("activity_log", JSONB, default=list),
    Column("histogram_data", JSONB, default=dict),
    Column("ml_stats", JSONB, default=dict),
)


class Database:
    async def connect(self):
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

    async def close(self):
        await engine.dispose()

    # USERS

    async def add_user(self, user_id: int, username: str):
        async with AsyncSessionLocal() as session:
            await session.execute(
                pg_insert(users)
                .values(
                    user_id=user_id,
                    username=username,
                    settings={},
                    progress={},
                    words_added={},
                    last_active=datetime.now(timezone.utc),
                    ml_profile={},
                )
                .on_conflict_do_nothing()
            )

            await session.execute(
                pg_insert(stats).values(user_id=user_id).on_conflict_do_nothing()
            )

            await session.commit()

    async def get_user(self, user_id: int):
        async with AsyncSessionLocal() as session:
            user_row = (
                await session.execute(select(users).where(users.c.user_id == user_id))
            ).fetchone()

            if not user_row:
                return None

            stats_row = (
                await session.execute(select(stats).where(stats.c.user_id == user_id))
            ).fetchone()

            user_stats = None
            if stats_row:
                user_stats = Stats(
                    user_id=user_id,
                    learned_words=stats_row.learned_words,
                    success_rate=stats_row.success_rate,
                    activity_log=stats_row.activity_log,
                    histogram_data=stats_row.histogram_data,
                    ml_stats=stats_row.ml_stats,
                )

            return User(
                user_id=user_row.user_id,
                username=user_row.username,
                settings=user_row.settings,
                progress=user_row.progress,
                words_added=user_row.words_added,
                last_active=user_row.last_active,
                stats=user_stats,
                ml_profile=user_row.ml_profile,
            )

    async def update_user_setting(self, user_id: int, key: str, value):
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(users.c.settings).where(users.c.user_id == user_id)
            )
            row = result.fetchone()
            current_settings = row.settings or {}
            current_settings[key] = value
            stmt = (
                update(users)
                .where(users.c.user_id == user_id)
                .values(settings=current_settings)
            )
            await session.execute(stmt)
            await session.commit()

    async def get_all_users(self):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(users))
            return result.fetchall()

    # WORDS

    async def add_word(self, word: str, translation: str, user_id: int):
        async with AsyncSessionLocal() as session:
            await session.execute(
                insert(words).values(
                    user_id=user_id,
                    text=word,
                    translation=translation,
                    next_repeat=datetime.now(timezone.utc) + timedelta(days=1),
                )
            )
            await session.commit()

    async def get_user_words(self, user_id: int):
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(words).where(words.c.user_id == user_id)
            )
            rows = result.fetchall()

            return [
                Word(
                    word_id=row.word_id,
                    user_id=row.user_id,
                    text=row.text,
                    translation=row.translation,
                    next_repeat=row.next_repeat,
                    repeat_count=row.repeat_count,
                    created_at=row.created_at,
                    base_difficulty=row.base_difficulty,
                    personal_difficulty=row.personal_difficulty,
                    difficulty=row.difficulty,
                    stability=row.stability,
                    ml_score=row.ml_score,
                    history=row.history,
                )
                for row in rows
            ]

    async def update_word_next_repeat(
        self, user_id: int, word_id: int, next_repeat=None
    ):
        if next_repeat is None:
            next_repeat = datetime.now(timezone.utc) + timedelta(days=1)

        async with AsyncSessionLocal() as session:
            await session.execute(
                update(words)
                .where(words.c.word_id == word_id, words.c.user_id == user_id)
                .values(next_repeat=next_repeat)
            )
            await session.commit()

    # STATS

    async def log_activity(self, user_id: int, action: str):
        async with AsyncSessionLocal() as session:
            new_activity = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": action,
            }

            result = await session.execute(
                select(stats.c.activity_log).where(stats.c.user_id == user_id)
            )
            row = result.fetchone()

            if row and row.activity_log:
                activity_log = list(row.activity_log)
            else:
                activity_log = []

            activity_log.append(new_activity)

            await session.execute(
                pg_insert(stats)
                .values(
                    user_id=user_id,
                    activity_log=activity_log,
                )
                .on_conflict_do_update(
                    index_elements=["user_id"],
                    set_={"activity_log": activity_log},
                )
            )

            await session.commit()

    async def get_user_stats(self, user_id: int):
        async with AsyncSessionLocal() as session:
            row = (
                await session.execute(select(stats).where(stats.c.user_id == user_id))
            ).fetchone()

            if not row:
                return None

            return Stats(
                user_id=row.user_id,
                learned_words=row.learned_words,
                success_rate=row.success_rate,
                activity_log=row.activity_log,
                histogram_data=row.histogram_data,
                ml_stats=row.ml_stats,
            )

    async def update_word_after_check(
        self,
        user_id: int,
        word_id: int,
        next_repeat: datetime,
        personal_difficulty: float,
        stability: float,
        ml_score: float,
        repeat_count: int,
    ):
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(words)
                .where(words.c.word_id == word_id, words.c.user_id == user_id)
                .values(
                    next_repeat=next_repeat,
                    personal_difficulty=personal_difficulty,
                    stability=stability,
                    ml_score=ml_score,
                    repeat_count=repeat_count,
                )
            )
            await session.commit()
