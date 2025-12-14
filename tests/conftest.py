import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from aiogram.types import User, Chat, Message
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_message():
    def create_message(text="", user_id=123):
        message = MagicMock(spec=Message)
        message.message_id = 1
        message.date = datetime.now(timezone.utc)
        message.text = text

        message.from_user = MagicMock()
        message.from_user.id = user_id
        message.from_user.username = "test_user"
        message.from_user.first_name = "Test"

        message.chat = MagicMock()
        message.chat.id = 456
        message.chat.type = "private"

        message.answer = AsyncMock()
        message.bot = MagicMock()
        return message
    return create_message


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.add_word = AsyncMock()
    db.get_user = AsyncMock()
    db.log_activity = AsyncMock()
    db.get_words_for_user = AsyncMock(return_value=[])
    return db

@pytest.fixture
def mock_bot():
    bot = MagicMock()
    bot["db"] = MagicMock()
    return bot
