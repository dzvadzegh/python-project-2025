from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import Table, MetaData, Column, Integer, String, DateTime, Float, JSON, insert, update, select
from datetime import datetime, timezone, timedelta
from infrastructure.config import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

metadata = MetaData()

users = Table('users', metadata,
    Column('user_id', Integer, primary_key=True),
    Column('username', String),
    Column('settings', JSON, default={}),
    Column('progress', JSON, default={}),
    Column('words_added', JSON, default={}),
    Column('last_active', DateTime, default=datetime.utcnow),
    Column('ml_profile', JSON, default={})
)

words = Table('words', metadata,
    Column('word_id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer),
    Column('text', String),
    Column('translation', String),
    Column('next_repeat', DateTime, default=datetime.utcnow),
    Column('repeat_count', Integer, default=0),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('base_difficulty', Float, default=0.5),
    Column('personal_difficulty', Float, default=0.5),
    Column('difficulty', Float, default=0.5),
    Column('stability', Float, default=1.0),
    Column('ml_score', Float, default=0.5),
    Column('history', JSON, default=[])
)

stats = Table('stats', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer),
    Column('learned_words', Integer, default=0),
    Column('success_rate', Float, default=0.0),
    Column('activity_log', JSON, default=[]),
    Column('histogram_data', JSON, default={}),
    Column('ml_stats', JSON, default={})
)


class Database:
    def __init__(self):
        self.session = None

    async def connect(self):
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

    async def close(self):
        if self.session:
            await self.session.close()
        await engine.dispose()

    async def get_db(self):
        if not self.session:
            self.session = AsyncSessionLocal()
        return self.session

    async def add_user(self, user_id: int, username: str):
        async with self.get_db() as session:
            stmt = insert(users).values(
                user_id=user_id,
                username=username,
                settings={},
                progress={},
                words_added={},
                last_active=datetime.now(timezone.utc),
                ml_profile={}
            ).on_conflict_do_nothing()

            await session.execute(stmt)

            stats_stmt = insert(stats).values(
                user_id=user_id,
                learned_words=0,
                success_rate=0.0,
                activity_log=[],
                histogram_data={},
                ml_stats={}
            )
            await session.execute(stats_stmt)

            await session.commit()

    async def get_user(self, user_id: int):
        async with self.get_db() as session:
            user_stmt = select(users).where(users.c.user_id == user_id)
            user_result = await session.execute(user_stmt)
            user_data = user_result.fetchone()

            if not user_data:
                return None

            stats_stmt = select(stats).where(stats.c.user_id == user_id)
            stats_result = await session.execute(stats_stmt)
            stats_data = stats_result.fetchone()

            from models.user import User
            from models.stats import Stats

            user_stats = None
            if stats_data:
                user_stats = Stats(
                    user_id=user_id,
                    learned_words=stats_data.learned_words,
                    success_rate=stats_data.success_rate,
                    activity_log=stats_data.activity_log,
                    histogram_data=stats_data.histogram_data,
                    ml_stats=stats_data.ml_stats
                )

            return User(
                user_id=user_data.user_id,
                username=user_data.username,
                settings=user_data.settings,
                progress=user_data.progress,
                words_added=user_data.words_added,
                last_active=user_data.last_active,
                stats=user_stats,
                ml_profile=user_data.ml_profile
            )

    async def add_word(self, word: str, translation: str, user_id: int):
        async with self.get_db() as session:
            stmt = insert(words).values(
                user_id=user_id,
                text=word,
                translation=translation,
                next_repeat=datetime.now(timezone.utc),
                repeat_count=0,
                created_at=datetime.now(timezone.utc),
                base_difficulty=0.5,
                personal_difficulty=0.5,
                difficulty=0.5,
                stability=1.0,
                ml_score=0.5,
                history=[]
            )
            await session.execute(stmt)
            await session.commit()

    async def get_words_for_review(self, user_id: int):
        async with self.get_db() as session:
            stmt = select(words).where(
                words.c.user_id == user_id,
                words.c.next_repeat <= datetime.now(timezone.utc)
            ).order_by(words.c.next_repeat)

            result = await session.execute(stmt)
            rows = result.fetchall()

            from models.word import Word as WordModel
            word_objects = []

            for row in rows:
                word_obj = WordModel(
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
                    history=row.history
                )
                word_objects.append(word_obj)

            return word_objects

    async def update_word_stats(self, word_id: int, repeat_count: int, difficulty: float):
        async with self.get_db() as session:
            stmt = update(words).where(words.c.word_id == word_id).values(
                repeat_count=repeat_count,
                difficulty=difficulty
            )
            await session.execute(stmt)
            await session.commit()

    async def update_word_full(self, word):
        async with self.get_db() as session:
            stmt = update(words).where(words.c.word_id == word.id).values(
                repeat_count=word.repeat_count,
                base_difficulty=word.base_difficulty,
                personal_difficulty=word.personal_difficulty,
                difficulty=word.difficulty,
                stability=word.stability,
                ml_score=word.ml_score,
                next_repeat=word.next_repeat,
                history=word.history
            )
            await session.execute(stmt)
            await session.commit()

    async def get_all_words(self):
        async with self.get_db() as session:
            stmt = select(words)
            result = await session.execute(stmt)
            rows = result.fetchall()

            from models.word import Word as WordModel
            return [
                WordModel(
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
                    history=row.history
                )
                for row in rows
            ]

    async def add_stat(self, user_id: int, score: int):
        async with self.get_db() as session:
            from sqlalchemy.dialects.postgresql import insert as pg_insert

            stmt = pg_insert(stats).values(
                user_id=user_id,
                learned_words=score
            ).on_conflict_do_update(
                index_elements=['user_id'],
                set_={'learned_words': stats.c.learned_words + score}
            )

            await session.execute(stmt)
            await session.commit()

    async def log_activity(self, user_id: int, action: str):
        async with self.get_db() as session:
            from sqlalchemy.dialects.postgresql import insert as pg_insert

            new_activity = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'action': action
            }

            stmt = pg_insert(stats).values(
                user_id=user_id,
                activity_log=[new_activity]
            ).on_conflict_do_update(
                index_elements=['user_id'],
                set_={
                    'activity_log': stats.c.activity_log.op('||')([new_activity])
                }
            )

            await session.execute(stmt)
            await session.commit()

    async def get_user_stats(self, user_id: int):
        async with self.get_db() as session:
            stmt = select(stats).where(stats.c.user_id == user_id)
            result = await session.execute(stmt)
            row = result.fetchone()

            if not row:
                return None

            from models.stats import Stats as StatsModel
            return StatsModel(
                user_id=row.user_id,
                learned_words=row.learned_words,
                success_rate=row.success_rate,
                activity_log=row.activity_log,
                histogram_data=row.histogram_data,
                ml_stats=row.ml_stats
            )

    async def get_all_users(self):
        async with self.get_db() as session:
            stmt = select(users)
            result = await session.execute(stmt)
            rows = result.fetchall()

            from models.user import User
            users_list = []

            for row in rows:
                stats_stmt = select(stats).where(stats.c.user_id == row.user_id)
                stats_result = await session.execute(stats_stmt)
                stats_row = stats_result.fetchone()

                from models.stats import Stats
                user_stats = None
                if stats_row:
                    user_stats = Stats(
                        user_id=row.user_id,
                        learned_words=stats_row.learned_words,
                        success_rate=stats_row.success_rate,
                        activity_log=stats_row.activity_log,
                        histogram_data=stats_row.histogram_data,
                        ml_stats=stats_row.ml_stats
                    )

                user_obj = User(
                    user_id=row.user_id,
                    username=row.username,
                    settings=row.settings,
                    progress=row.progress,
                    words_added=row.words_added,
                    last_active=row.last_active,
                    stats=user_stats,
                    ml_profile=row.ml_profile
                )
                users_list.append(user_obj)

            return users_list

    async def get_user_words(self, user_id: int):
        async with self.get_db() as session:
            stmt = select(words).where(words.c.user_id == user_id)
            result = await session.execute(stmt)
            rows = result.fetchall()

            from models.word import Word as WordModel
            return [
                WordModel(
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
                    history=row.history
                )
                for row in rows
            ]

    async def update_word_next_repeat(self, user_id: int, word_id: int, next_repeat=None):
        if next_repeat is None:
            next_repeat = datetime.now(timezone.utc) + timedelta(days=1)

        async with self.get_db() as session:
            stmt = update(words).where(
                words.c.word_id == word_id,
                words.c.user_id == user_id
            ).values(next_repeat=next_repeat)

            await session.execute(stmt)
            await session.commit()

    async def update_user_setting(self, user_id: int, key: str, value):
        async with self.get_db() as session:
            from sqlalchemy import func

            stmt = update(users).where(users.c.user_id == user_id).values(
                settings=func.jsonb_set(
                    func.coalesce(users.c.settings, {}),
                    [key],
                    value,
                    True
                )
            )

            await session.execute(stmt)
            await session.commit()

    async def get_word_by_id(self, word_id: int):
        async with self.get_db() as session:
            stmt = select(words).where(words.c.word_id == word_id)
            result = await session.execute(stmt)
            row = result.fetchone()

            if not row:
                return None

            from models.word import Word as WordModel
            return WordModel(
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
                history=row.history
            )