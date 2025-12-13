import asyncpg
from datetime import datetime, timezone, timedelta
from infrastructure.config import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            host=DB_HOST,
            port=DB_PORT,
        )

    async def close(self):
        await self.pool.close()

    async def add_user(self, user_id: int, username: str):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users (user_id, username, settings, progress, words_added)
                VALUES ($1, $2, '{}'::jsonb, '{}'::jsonb, '{}'::jsonb)
                ON CONFLICT (user_id) DO NOTHING
                """,
                user_id,
                username,
            )

    async def get_user(self, user_id: int):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM users WHERE user_id = $1", user_id
            )

    async def add_word(self, word: str, translation: str, user_id: int):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO words (user_id, text, translation)
                VALUES ($1, $2, $3)
                """,
                user_id,
                word,
                translation,
            )

    async def get_words_for_review(self, user_id: int):
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                """
                SELECT * FROM words
                WHERE user_id = $1
                AND next_repeat <= NOW()
                ORDER BY next_repeat ASC
                """,
                user_id,
            )

    async def update_word_stats(
        self, word_id: int, repeat_count: int, difficulty: float
    ):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE words
                SET repeat_count = $2,
                    difficulty = $3
                WHERE id = $1
                """,
                word_id,
                repeat_count,
                difficulty,
            )

    async def get_all_words(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch("SELECT * FROM words")

    async def add_stat(self, user_id: int, score: int):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO stats (user_id, score)
                VALUES ($1, $2)
                """,
                user_id,
                score,
            )

    async def log_activity(self, user_id: int, action: str):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE stats
                SET activity_log = COALESCE(activity_log, '[]'::jsonb)
                    || jsonb_build_array(jsonb_build_object(
                        'timestamp', NOW(),
                        'action', $2
                    ))
                WHERE user_id = $1
                """,
                user_id,
                action,
            )

    async def get_user_stats(self, user_id: int):
        async with self.pool.acquire() as conn:
            return await conn.fetch("SELECT * FROM stats WHERE user_id = $1", user_id)

    async def get_all_users(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch("SELECT * FROM users")

    async def get_user_words(self, user_id: int):
        async with self.pool.acquire() as conn:
            return await conn.fetch("SELECT * FROM words WHERE user_id = $1", user_id)

    async def update_word_next_repeat(
        self, user_id: int, word_id: int, next_repeat=None
    ):
        if next_repeat is None:
            next_repeat = datetime.now(timezone.utc) + timedelta(days=1)
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE words SET next_repeat=$1 WHERE user_id=$2 AND id=$3",
                next_repeat,
                user_id,
                word_id,
            )
